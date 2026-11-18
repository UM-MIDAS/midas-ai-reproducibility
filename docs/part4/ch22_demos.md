# Chapter 22: Interactive Demos and Web Apps

:::{admonition} What You Will Learn
:class: tip

- Why a demo is often the most effective way to share a model
- How to build a minimal demo with Gradio or Streamlit
- Where to host demos, and what current free options offer
- How to make demos accessible
- How to keep demos running, or retire them gracefully
:::

## Why Demos Matter

Most people who might benefit from your model will never clone your repository. A colleague in another department, a program officer, a journalist, a policymaker, a community partner, or a reviewer skimming your paper wants to know one thing first: what does it do? A demo, a small web page where they can upload an image or type some text and see the model's output, answers that question in thirty seconds.

Demos also serve research purposes. They let domain experts probe a model's behavior on examples they care about, which often surfaces failure modes that benchmark metrics miss. They are a natural way to share models that cannot be released as weights, for example because of the privacy concerns in Chapter 19. And a linked demo substantially increases how many people engage with a model on Hugging Face.

The Model Zoo already includes a web application, the Clinical Trial Randomization Tool, which shows how a research method can be made usable by people who will never write code.

## Gradio and Streamlit

Two Python libraries make it possible to build a demo in a few lines of code, with no web development experience.

### Gradio

Gradio is designed for machine learning demos. You write a Python function that takes inputs and returns outputs, and Gradio builds a web interface around it.

```python
# app.py
import gradio as gr
from my_model import load_model

model = load_model("your-lab/roof-condition-classifier", revision="v1.0")

def classify(image):
    """Return class probabilities for a street-level photo of a house."""
    return model.predict_proba(image)   # dict of {label: probability}

demo = gr.Interface(
    fn=classify,
    inputs=gr.Image(type="pil", label="Photo of a house"),
    outputs=gr.Label(num_top_classes=4, label="Predicted roof condition"),
    title="Roof Condition Classifier",
    description="Upload a street-level photo. Research prototype; see the model card for limitations.",
    examples=["examples/house_01.jpg", "examples/house_02.jpg"],
)

if __name__ == "__main__":
    demo.launch()
```

Run `python app.py` and open the local address it prints. The `examples` argument lets visitors try the model with one click, without needing their own image. Gradio also automatically exposes an API for each demo, so other researchers can call your model programmatically.

For more complex layouts, Gradio's `Blocks` interface gives finer control over arrangement and interaction.

### Hands-On: A Blocks Demo Built for Everyone

This version uses `Blocks` to add three things the simple version lacks: an explicit disclaimer and link to the model card, a plain-language text summary of every prediction (which screen reader users can read directly, and which is easier for everyone to quote), and descriptive labels for the example images:

```python
# app.py: an accessible Gradio demo with a text summary of every prediction
import gradio as gr

LABELS = ["intact", "minor damage", "major damage", "missing"]

def classify(image):
    """Return class probabilities and a plain-language summary of them."""
    if image is None:
        return {}, "Please upload a photo first."
    probs = [0.70, 0.20, 0.07, 0.03]          # replace with model.predict_proba(image)
    ranked = sorted(zip(LABELS, probs), key=lambda kv: kv[1], reverse=True)
    summary = (f"Most likely: {ranked[0][0]} ({ranked[0][1]:.0%}). "
               f"Next: {ranked[1][0]} ({ranked[1][1]:.0%}).")
    return dict(ranked), summary

with gr.Blocks(title="Roof Condition Classifier") as demo:
    gr.Markdown(
        "# Roof Condition Classifier\n"
        "Upload a street-level photo of a house to estimate its roof condition. "
        "**Research prototype.** Trained on three Midwestern cities; see the "
        "[model card](https://huggingface.co/your-lab/roof-condition-classifier) for limitations. "
        "Uploaded photos are not stored.")
    with gr.Row():
        image = gr.Image(type="pil", label="Photo of a house (JPG or PNG)")
        with gr.Column():
            probs = gr.Label(num_top_classes=4, label="Predicted roof condition")
            summary = gr.Textbox(label="Result in words", interactive=False)
    button = gr.Button("Classify photo", variant="primary")
    button.click(classify, inputs=image, outputs=[probs, summary], api_name="predict")
    gr.Examples(examples=["examples/house_01.jpg", "examples/house_02.jpg"],
                example_labels=["House with an intact roof", "House with a damaged roof (known failure case)"],
                inputs=image, label="Example photos")

if __name__ == "__main__":
    demo.launch()
```

The `api_name="predict"` argument gives the demo a stable programmatic endpoint. Anyone, including your own health checks, can call it with the `gradio_client` library:

```python
from gradio_client import Client, handle_file
client = Client("your-lab/roof-condition-demo")          # a Space name or a URL
print(client.predict(handle_file("examples/house_01.jpg"), api_name="/predict"))
```

```text
({'label': 'intact', 'confidences': [{'label': 'intact', 'confidence': 0.7}, ...]},
 'Most likely: intact (70%). Next: minor damage (20%).')
```

### Streamlit

Streamlit is a general-purpose framework for data apps. It is a good fit when your demo is closer to a dashboard, with charts, filters, and explanations, than a single input-output function.

```python
# streamlit_app.py
import streamlit as st
from PIL import Image
from my_model import load_model

st.title("Roof Condition Classifier")
st.caption("Research prototype. See the model card for intended uses and limitations.")

@st.cache_resource
def get_model():
    return load_model("your-lab/roof-condition-classifier", revision="v1.0")

uploaded = st.file_uploader("Upload a street-level photo of a house", type=["jpg", "png"])
if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Your uploaded photo")
    st.bar_chart(get_model().predict_proba(image))
```

Run with `streamlit run streamlit_app.py`.

**Shiny**, available for both R and Python, is a good choice if you or your users work primarily in R.

### Include the Model Card Essentials

Every demo should say, near the top, what the model is for, that it is a research prototype (if it is), and where to find the model card and paper. People who try a demo tend to assume it works well on anything they give it. A sentence on limitations sets appropriate expectations, and examples chosen to show both successes and known failures are even more informative.

If the demo collects user inputs, say so, and do not store uploads unless you have a clear reason and have told users. Do not deploy a demo that encourages people to upload sensitive information, such as medical images or personal documents, without appropriate review.

## Hosting

A demo running on your laptop is not shared. Hosting options include:

**Hugging Face Spaces.** Spaces host Gradio, Streamlit (via Docker), and static HTML apps directly from a Git repository, and link naturally to your model and dataset repositories. The free CPU hardware tier provides 2 virtual CPUs and 16 GB of RAM, and free Spaces go to sleep when unused and wake on the next visit. Hosting policies have changed recently: at the time of writing, Gradio and Docker Spaces running on compute require a paid plan (PRO for personal accounts, or a Team or Enterprise organization), with the exception that free personal accounts can host a small number of Gradio Spaces on **ZeroGPU**, a shared GPU pool. Static HTML Spaces are free for everyone. Check the current Spaces documentation before planning a demo, and consider whether your lab or MIDAS has an organization plan you can use.

**Streamlit Community Cloud** hosts public Streamlit apps from GitHub repositories for free, with resource limits and sleeping when inactive.

**shinyapps.io** and **Posit Connect** host Shiny apps, with a limited free tier on shinyapps.io.

**Static demos.** Some models can run entirely in the user's browser, using libraries such as Transformers.js or ONNX Runtime Web. A static page can then be hosted for free on GitHub Pages or a static Space, with no server at all. This works well for small models, and has the added benefit that user inputs never leave their device.

```html
<!-- index.html: a sentiment model that runs entirely in the visitor's browser -->
<main>
  <h1>Sentiment demo</h1>
  <label for="text">Text to classify</label>
  <textarea id="text" rows="3"></textarea>
  <button id="go">Classify</button>
  <p id="result" aria-live="polite">Loading model...</p>
</main>
<script type="module">
  // Pin an exact version in real use, e.g. @huggingface/transformers@3.x.y
  import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3";
  const classify = await pipeline("sentiment-analysis",
                                  "Xenova/distilbert-base-uncased-finetuned-sst-2-english");
  const result = document.getElementById("result");
  result.textContent = "Ready.";
  document.getElementById("go").onclick = async () => {
    const [out] = await classify(document.getElementById("text").value);
    result.textContent = `${out.label} (${(out.score * 100).toFixed(0)}% confidence)`;
  };
</script>
```

The `aria-live="polite"` attribute makes screen readers announce the result when it appears, and the `<label>` element names the text box for assistive technology. The model downloads once to the visitor's browser cache, so the first prediction is slow and later ones are fast. Your own models can be served this way after conversion to ONNX (Chapter 21).

**Institutional hosting.** For long-running or heavily used tools, or those handling sensitive inputs, institutional hosting may be more appropriate. Talk to MIDAS or your unit's IT staff about options at U-M.

## Accessible Demos

Demos are web pages, so the accessibility requirements in Chapter 23 apply to them. Gradio and Streamlit handle some basics for you, but not everything. Check that:

- **Every input and output has a descriptive label.** Use the `label` arguments in Gradio and the label parameters in Streamlit widgets, rather than relying on nearby text.
- **The app can be used with a keyboard alone.** Tab through it and make sure every control can be reached and operated.
- **Images have text alternatives.** Example images should have descriptive captions or alt text. Model outputs that are images (such as generated images or heatmaps) should be accompanied by a text summary where possible.
- **Color is not the only way information is conveyed.** If a chart uses colors for classes, also label them directly (Chapter 23).
- **Contrast is sufficient.** Custom themes can easily produce low-contrast text.
- **Text is plain.** Descriptions should be understandable by non-specialists.

Run an automated checker such as axe or WAVE on the running demo, and fix what it finds (Chapter 23). Do not assume a framework takes care of accessibility for you. When we ran the axe checker (using the script in Chapter 23) on the Blocks demo above without the `example_labels` argument, it reported:

```text
[serious] aria-prohibited-attr: Elements must only use permitted ARIA attributes (1 element(s))
[critical] button-name: Buttons must have discernible text (2 element(s))
[serious] color-contrast: Elements must meet minimum color contrast ratio thresholds (5 element(s))
[serious] label-content-name-mismatch: Elements must have their visible text as part of their accessible name (1 element(s))

4 rule(s) violated, 24 passed
```

The critical problem was ours: the example images were buttons with no text, so a screen reader announced them only as "button." Adding `example_labels` fixed it. The other three issues come from Gradio's built-in components (tested with Gradio 6.32), such as the light gray "- or -" text in the image upload box. You can address contrast with a custom theme or CSS, and report component-level issues to the framework's maintainers. Record known remaining issues in the demo's README, and re-run the check when you upgrade the framework, since results change from version to version.

## Keeping Demos Alive

Demos are the most fragile shared artifact. They depend on a running server, an unpinned environment, and often a hosting plan that can change.

**Pin everything.** Use a `requirements.txt` with exact versions or a Dockerfile (Chapters 5 and 6), and load the model at a pinned revision. An unpinned demo will eventually break when a library updates. On Hugging Face Spaces, the Gradio version is set in the YAML header of the Space's `README.md`, and other packages in `requirements.txt`:

```yaml
---
title: Roof Condition Classifier
sdk: gradio
sdk_version: 6.32.0          # pin the exact Gradio version you tested
python_version: "3.11"
app_file: app.py
models:
  - your-lab/roof-condition-classifier   # links the Space to the model page
license: apache-2.0
---
```

```text
# requirements.txt for the Space
torch==2.4.1
safetensors==0.4.5
huggingface_hub==2.4.0
```

Use the versions you actually tested with, from your lockfile, rather than the illustrative numbers here.

**Monitor it.** Add the demo URL to the health check from Chapter 20. For sleeping Spaces, a check that loads the page will also wake it. Better still, call the demo's API with a known example and compare the answer, which confirms that the model is actually working, not just that the page loads:

```python
from gradio_client import Client, handle_file
label, summary = Client("your-lab/roof-condition-demo").predict(
    handle_file("tests/data/house_01.jpg"), api_name="/predict")
assert label["label"] == "intact", f"Demo answer changed: {label}"
```

**Control cost.** If you pay for GPU hardware, set it to sleep after inactivity. A forgotten GPU Space can run up significant charges.

**Plan for retirement.** Demos are rarely meant to last forever. When you stop maintaining one, replace it with a static page that explains what it did, shows example inputs and outputs, and links to the model and code. Update the Model Zoo entry.

## Try This

Build a Gradio demo for a model you have trained, using the template above. Include two or three example inputs, one of which shows a known limitation. Run it locally, then check it with a keyboard only and with the axe browser extension. Finally, decide where to host it given current options, and add a link to it from your model card.

## Further Reading

The Gradio, Streamlit, and Shiny documentation each include quickstart guides and galleries of example apps. The Hugging Face Spaces documentation describes current hardware, pricing, and ZeroGPU availability.

## In the Model Zoo

Web applications are a Model Zoo category in their own right. For other entries, a hosted demo is one way to meet the proposed "Accessible" tier.

## Related Chapters

- [Chapter 14: Sharing on Hugging Face](../part3/ch14_hugging_face.md)
- [Chapter 21: AI on Modest Hardware](ch21_low_resource.md)
- [Chapter 23: Disability Accessibility for Research Outputs](ch23_disability_access.md)

---

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
