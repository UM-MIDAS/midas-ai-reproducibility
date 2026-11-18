# Chapter 23: Disability Accessibility for Research Outputs

:::{admonition} What You Will Learn
:class: tip

- Which accessibility standards apply to university research outputs, and why they now carry legal weight
- How to make figures and visualizations accessible, including alt text and color choices
- How to make notebooks, documentation sites, PDFs, and videos accessible
- How AI can help draft accessibility content, and why humans must review it
- Tools for checking your work
:::

## Who Can Use Your Work?

The previous chapters asked whether people can get your work and whether they can run it. This chapter asks whether they can use it at all. About one in four U.S. adults reports some form of disability. Among the people who might read your paper, use your dataset, follow your tutorial, or try your demo are researchers and students who are blind or have low vision and use screen readers or magnification, who are colorblind, who are deaf or hard of hearing, who cannot use a mouse, or who have cognitive or learning disabilities.

A chart that encodes its key finding only in red and green is unreadable to roughly one in twelve men with red-green color vision deficiency. A tutorial video without captions excludes deaf viewers. A Jupyter notebook where every result is an image with no description gives a screen reader user nothing. A demo app that requires dragging and dropping with a mouse is unusable by someone navigating with a keyboard.

Most of these barriers are easy to avoid when you know to look for them. They are also widespread: the 2026 WebAIM Million report found detectable accessibility failures on 95.9% of the top one million website home pages, with low-contrast text, missing image alternative text, and missing form labels the most common problems {footcite}`webaim2026`. Those same problems appear in research outputs.

## Why This Is Required, Not Optional

Accessibility has long been an ethical expectation and a matter of university policy. For public universities in the United States, it is now also a specific legal requirement for web content.

In April 2024, the U.S. Department of Justice issued a rule under Title II of the Americans with Disabilities Act requiring state and local government entities, which include public universities such as the University of Michigan, to make their web content and mobile apps conform to the **Web Content Accessibility Guidelines (WCAG) 2.1, Level AA**. In April 2026, the Department issued an interim final rule extending the compliance dates by one year: to **April 26, 2027** for entities serving populations of 50,000 or more (which includes large public universities) and April 26, 2028 for smaller entities. The Department emphasized that the extension changes only the dates, and that the underlying obligations remain in force.

The rule covers web content that a public university provides or makes available, which can include course materials, documentation, public-facing web applications, and documents posted online. It includes limited exceptions, for example for some archived content. How the rule applies to specific research outputs, such as a model demo or documentation site hosted on a third-party platform, is a question for your institution's accessibility and compliance offices. U-M's digital accessibility resources are a good starting point. Regardless of the legal details, following the practices in this chapter is the right thing to do and will put your work in good shape.

## WCAG in Brief

WCAG is organized around four principles, often remembered as **POUR**:

**Perceivable.** Information must be presentable in ways users can perceive: text alternatives for images, captions for video, sufficient contrast, and not relying on color alone.

**Operable.** Interfaces must be usable with a keyboard and other input methods, give users enough time, and avoid content that can cause seizures.

**Understandable.** Text should be readable, pages should behave predictably, and forms should help users avoid and correct errors.

**Robust.** Content should work with assistive technologies, which mostly means using standard, well-structured markup.

Each principle has specific success criteria at levels A, AA, and AAA. Level AA is the target in the Title II rule and most institutional policies. You do not need to memorize the criteria; the practices below cover the ones that most often matter for research outputs.

## Figures and Visualizations

Figures are central to research communication and are one of the most common barriers.

### Alt Text and Long Descriptions

Every informative image needs a **text alternative** that conveys its content and purpose to someone who cannot see it. For a photograph, a short description is enough. For a chart, alt text should convey the key message, not just the chart type.

- Weak: "Line chart of results."
- Better: "Line chart showing validation accuracy over 20 epochs for three models. The fine-tuned model reaches 91% by epoch 8 and plateaus; both baselines stay below 80%."

For complex figures, provide a short alt text plus a **long description** or the underlying data table nearby. Linking to the data (as a CSV or table) is often the most useful alternative, since it lets screen reader users explore the values themselves.

Purely decorative images should have empty alt text (`alt=""`) so screen readers skip them.

How to add alt text depends on the format:

- **Markdown and MyST** (as in this handbook): `![Line chart showing ...](figure.png)` or the `:alt:` option on an image directive.
- **HTML**: the `alt` attribute on `<img>`.
- **Word and PowerPoint**: right-click the image and choose the alt text option.
- **LaTeX**: support is improving through the LaTeX tagged-PDF project; check the current status for your distribution, or provide descriptions in the text and the figure caption.
- **Hugging Face and GitHub READMEs**: Markdown alt text, as above.

### Color

Around 8% of men and 0.5% of women have some form of color vision deficiency, most commonly difficulty distinguishing red and green. Some common scientific color maps also distort data and are hard to read for everyone {footcite}`crameri2020`.

- **Use colorblind-safe palettes.** The Okabe–Ito palette works well for categorical data. For continuous data, use perceptually uniform color maps such as viridis, cividis, or the scientific color maps by Crameri. Avoid rainbow ("jet") color maps.
- **Do not rely on color alone.** Add a second cue: different line styles or marker shapes, direct labels on lines instead of a separate legend, or patterns in bars.
- **Check contrast.** WCAG AA requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text and for graphical objects needed to understand content, such as chart lines against their background.
- **Simulate.** Tools such as Color Oracle or online simulators show how your figure looks with different kinds of color vision.

In matplotlib, you can apply these defaults at the start of a script:

```python
import matplotlib.pyplot as plt
okabe_ito = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#000000"]
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=okabe_ito)
plt.rcParams["image.cmap"] = "viridis"
```

### Hands-On: Check Contrast Yourself

WCAG defines contrast with a formula you can compute in a few lines, which is handy for checking a palette, a theme, or a figure's colors before you publish:

```python
def relative_luminance(hex_color):
    """WCAG 2.x relative luminance of a color like '#1f77b4'."""
    rgb = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

def contrast_ratio(fg, bg="#ffffff"):
    l1, l2 = sorted([relative_luminance(fg), relative_luminance(bg)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

okabe_ito = {"orange": "#E69F00", "sky blue": "#56B4E9", "bluish green": "#009E73",
             "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00",
             "reddish purple": "#CC79A7", "black": "#000000"}
for name, hex_color in okabe_ito.items():
    r = contrast_ratio(hex_color)
    verdict = "ok for lines and marks" if r >= 3 else "too light on white: add outlines or use for fills only"
    print(f"{name:15} {hex_color}  {r:5.2f}:1  {verdict}")
print(f"\ngray text #777777 on white: {contrast_ratio('#777777'):.2f}:1 (normal text needs 4.5:1)")
```

```text
orange          #E69F00   2.25:1  too light on white: add outlines or use for fills only
sky blue        #56B4E9   2.31:1  too light on white: add outlines or use for fills only
bluish green    #009E73   3.42:1  ok for lines and marks
yellow          #F0E442   1.32:1  too light on white: add outlines or use for fills only
blue            #0072B2   5.19:1  ok for lines and marks
vermillion      #D55E00   3.87:1  ok for lines and marks
reddish purple  #CC79A7   3.06:1  ok for lines and marks
black           #000000  21.00:1  ok for lines and marks

gray text #777777 on white: 4.48:1 (normal text needs 4.5:1)
```

This reveals a subtlety. The Okabe–Ito colors are chosen to be distinguishable from each other by people with color vision deficiencies, but four of them are too light to meet the 3:1 contrast requirement for lines and markers on a white background. They remain fine for filled areas such as bars with a dark outline, or on a dark background. For thin lines on white, prefer blue, vermillion, bluish green, reddish purple, and black. And a mid-gray that looks perfectly readable, `#777777`, just misses the 4.5:1 threshold for text.

### Hands-On: An Accessible Figure from Start to Finish

This example applies everything in this section to a typical results figure: colors that pass both color-vision and contrast checks, a different line style and marker for every series, direct labels instead of a legend, alt text saved with the figure, and the underlying data saved as a table:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Okabe-Ito colors that also reach 3:1 contrast against white
COLORS = {"Fine-tuned": "#0072B2", "Baseline A": "#D55E00", "Baseline B": "#000000"}
MARKERS = {"Fine-tuned": "o", "Baseline A": "s", "Baseline B": "^"}
STYLES = {"Fine-tuned": "-", "Baseline A": "--", "Baseline B": ":"}

epochs = np.arange(1, 21)
curves = {"Fine-tuned": 0.91 - 0.35 * np.exp(-epochs / 2.5),
          "Baseline A": 0.79 - 0.30 * np.exp(-epochs / 4),
          "Baseline B": 0.74 - 0.25 * np.exp(-epochs / 5)}

fig, ax = plt.subplots(figsize=(6, 3.8), dpi=150)
for name, acc in curves.items():
    ax.plot(epochs, acc, color=COLORS[name], linestyle=STYLES[name], marker=MARKERS[name],
            markevery=4, linewidth=2)
    ax.annotate(f"{name} ({acc[-1]:.0%})", xy=(epochs[-1], acc[-1]), xytext=(6, 0),
                textcoords="offset points", va="center", fontsize=10, color=COLORS[name])
ax.set_xlabel("Epoch", fontsize=11)
ax.set_ylabel("Validation accuracy", fontsize=11)
ax.set_xlim(1, 27)                        # room for direct labels instead of a legend
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()

alt_text = ("Line chart of validation accuracy over 20 epochs for three models. "
            "The fine-tuned model rises fastest and plateaus at 91% by about epoch 10; "
            "Baseline A reaches 79% and Baseline B 74%.")
fig.savefig("accuracy_by_epoch.png", metadata={"Description": alt_text})
pd.DataFrame({"epoch": epochs, **{k: v.round(4) for k, v in curves.items()}}).to_csv(
    "accuracy_by_epoch.csv", index=False)               # the data behind the figure
open("accuracy_by_epoch.alt.txt", "w").write(alt_text)
```

The result:

```{image} ../_static/ch23_accessible_figure.png
:alt: Line chart of validation accuracy over 20 epochs for three models. The fine-tuned model rises fastest and plateaus at 91% by about epoch 10; Baseline A reaches 79% and Baseline B 74%.
:width: 90%
:align: center
```

To check how it looks to people with red-green color blindness, and in grayscale (for example, printed), simulate both with the `colorspacious` package:

```python
# Preview a figure in grayscale and as seen with deuteranopia (red-green color blindness)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from colorspacious import cspace_convert

img = plt.imread("accuracy_by_epoch.png")[..., :3]
deuter = np.clip(cspace_convert(img, {"name": "sRGB1+CVD", "cvd_type": "deuteranomaly",
                                       "severity": 100}, "sRGB1"), 0, 1)
gray = np.repeat(img @ np.array([0.2126, 0.7152, 0.0722]), 3).reshape(img.shape)

fig, axes = plt.subplots(1, 3, figsize=(15, 3.9), dpi=110)
for ax, picture, title in zip(axes, [img, deuter, gray], ["Original", "Deuteranopia", "Grayscale"]):
    ax.imshow(picture); ax.set_title(title, fontsize=13); ax.axis("off")
fig.tight_layout()
fig.savefig("accuracy_by_epoch_simulated.png")
```

```{image} ../_static/ch23_figure_simulated.png
:alt: The same accuracy chart shown three times, as originally rendered, as simulated for deuteranopia, and in grayscale. In all three versions the three lines can be told apart by line style, marker shape, and direct labels.
:width: 100%
:align: center
```

In the deuteranopia simulation, the blue and vermillion lines shift toward blue and olive but stay distinct, and in grayscale they become similar shades. They remain easy to tell apart in every version because the line styles, marker shapes, and labels carry the information as well as the color. That redundancy is the real goal. Notice also that the alt text above states the finding, not just the chart type, and that the CSV file gives screen reader users access to the exact values.

### Text in Figures

Use font sizes that remain legible when the figure is scaled down in a paper or slide, and avoid putting essential information only in tiny tick labels or annotations.

## Notebooks and Code

Jupyter notebooks are widely used for tutorials and for sharing analyses, and they present specific challenges for screen reader users.

- **Use Markdown headings** (`#`, `##`) to structure notebooks, so users can navigate by heading.
- **Add alt text** to images in Markdown cells.
- **Describe key outputs in text.** After a cell that produces a plot, add a Markdown cell summarizing what it shows. This also helps sighted readers.
- **Print key numbers** rather than showing them only in plots.
- **Use descriptive variable and function names** and comments. Code is read by screen readers too.
- **Avoid very long cells and outputs**, which are tedious to navigate.

JupyterLab has been improving its accessibility, and newer versions work better with screen readers. For published tutorials, consider also rendering notebooks to HTML with a documentation tool (Chapter 24), which usually produces more accessible output than the notebook interface.

## Documentation Sites and PDFs

**Web documentation** (such as sites built with Sphinx, MkDocs, or Quarto) is usually easier to make accessible than PDFs. Use headings in order without skipping levels, write descriptive link text ("see the installation guide" instead of "click here"), use real tables for tabular data with header rows, and provide alt text for every image. Choose a theme that has been tested for accessibility, and check contrast if you customize colors.

**PDFs** are harder. An accessible PDF must be **tagged**, meaning it contains a structure that identifies headings, paragraphs, lists, tables, and figures, with alt text for images and a logical reading order. PDFs exported from Word or PowerPoint can be tagged if the source document uses built-in heading styles and alt text. Adobe Acrobat's accessibility checker can identify problems. Where possible, provide an HTML version alongside PDFs.

**Math** is best provided as MathML or rendered with MathJax or KaTeX in HTML, which screen readers can interpret, rather than as images of equations.

## Video and Audio

Workshop recordings and tutorial videos are an important way to share research methods.

- **Captions** are required for prerecorded video with audio. Automatic captions from Zoom, YouTube, or other tools are a good starting point, but they make errors, especially with technical terms, names, and code. Review and correct them. If you need to draft captions yourself, the open-source Whisper speech recognition model can produce a standard WebVTT caption file locally, so the recording never leaves your computer: `pip install openai-whisper`, then `whisper workshop.mp4 --model small --language en --output_format vtt`. Open the `.vtt` file in a text editor to correct names and technical terms before uploading it with the video.
- **Transcripts** help everyone, including people who prefer reading and people searching for a specific topic.
- **Describe what is shown.** When you demonstrate something on screen, say what you are doing ("I'm clicking the Settings tab, then Generate DOI") rather than "click here, then here." This helps blind viewers and makes videos more useful for everyone.
- **Share slides and code** alongside the recording.

## AI as an Accessibility Aid, With Checks

AI tools can help with accessibility work: drafting alt text for figures, generating captions and transcripts, suggesting plain-language rewrites, and checking color contrast. These uses can save significant time, particularly when making large collections of existing materials accessible.

But AI-generated accessibility content must be reviewed by a person who understands the material. Vision-language models often produce generic or inaccurate alt text for scientific figures: they may describe the chart type correctly but misread values, miss the key finding, or invent details. Automatic captions mishear technical vocabulary. An incorrect description can be worse than none, because the user has no way to know it is wrong.

A practical workflow is to have AI draft alt text or captions, then have the author, who knows what the figure is meant to show, edit the draft for accuracy and emphasis.

## Checking Your Work

Automated tools catch many common problems, but not all. Use them as a first pass, then do some manual checks.

**Automated checkers**

- **axe DevTools** and **WAVE** are browser extensions that check a web page and list problems with explanations.
- **Lighthouse**, built into Chrome's developer tools, includes an accessibility audit.
- **Accessibility Insights** (Microsoft) combines automated checks with guided manual tests.
- **Adobe Acrobat's** accessibility checker for PDFs, and the built-in accessibility checkers in Word and PowerPoint.
- **WebAIM's contrast checker** for color pairs.

### Hands-On: Run axe from a Script, on Every Page

Browser extensions check one page at a time. For documentation sites, demos, and anything you update regularly, it is more reliable to run the same axe engine from a script, so it can check every page, and run automatically in CI (Chapter 9):

```python
# scripts/axe_check.py: run the axe accessibility checker on a web page
#   pip install playwright && playwright install chromium
#   npm install axe-core          (provides node_modules/axe-core/axe.min.js)
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")
    page.add_script_tag(path="node_modules/axe-core/axe.min.js")
    results = page.evaluate("axe.run(document, {runOnly: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']})")
    browser.close()

for v in results["violations"]:
    print(f"[{v['impact']}] {v['id']}: {v['help']} ({len(v['nodes'])} element(s))")
    print(f"    e.g. {v['nodes'][0]['html'][:100]}")
print(f"\n{len(results['violations'])} rule(s) violated, {len(results['passes'])} passed")
sys.exit(1 if any(v["impact"] in ("serious", "critical") for v in results["violations"]) else 0)
```

```bash
pip install playwright && playwright install chromium
npm install axe-core
python scripts/axe_check.py https://your-lab.github.io/your-docs/
```

The script exits with an error when it finds serious or critical problems, so a CI job running it fails until they are fixed.

We ran this check on every page of this handbook while writing this chapter. The default Read the Docs theme failed on several WCAG 2.1 AA rules: white text on light-colored admonition headers (2.4:1 contrast), light gray footnote and footer text, links that differed from surrounding text only by color, sidebar headings missing an ARIA attribute, and code blocks and tables that keyboard users could not scroll. None of these were visible problems for a sighted mouse user, which is exactly why automated checks matter. The fixes took a few lines of CSS and JavaScript, which you can reuse in your own Sphinx projects: see `docs/_static/accessibility.css` and `docs/_templates/layout.html` in this handbook's repository. After the fixes, all 28 pages pass axe's automated WCAG 2.1 A and AA checks. Automated checks still cannot judge whether alt text is meaningful or whether a page makes sense to a screen reader user, so the manual checks below still apply.

**Manual checks**

- **Keyboard only.** Put away your mouse and try to use your page, demo, or documentation with Tab, Shift+Tab, Enter, Space, and arrow keys. Can you reach everything? Can you see where the focus is?
- **Screen reader spot check.** Try a free screen reader: NVDA on Windows, VoiceOver built into macOS and iOS, or TalkBack on Android. Listen to a page of your documentation or a figure with its alt text. It is often eye-opening.
- **Zoom to 200%.** Does the content still work without horizontal scrolling or overlapping text?
- **Grayscale.** View your figures in grayscale to check they do not depend on color.

## Try This

Take the figures from your most recent paper and check each one: does it have meaningful alt text, does it use a colorblind-safe palette, and does it convey its message without color? Then run axe or WAVE on your lab website or a documentation page for one of your tools, and try navigating it with only a keyboard. Fix the three most serious problems you find.

## Further Reading

The W3C's Web Accessibility Initiative (w3.org/WAI) publishes WCAG, along with plain-language introductions and tutorials. The WebAIM Million report {footcite}`webaim2026` shows which problems are most common. Crameri et al. {footcite}`crameri2020` explain problems with common scientific color maps and offer alternatives. For U-M-specific guidance and support, see U-M's digital accessibility resources.

## In the Model Zoo

For the proposed "Accessible" tier, documentation and demos should pass an automated accessibility check with no serious errors, figures in documentation should have alt text, and tutorial videos should have reviewed captions.

## Related Chapters

- [Chapter 22: Interactive Demos and Web Apps](ch22_demos.md)
- [Chapter 24: Accessible Documentation and Teaching Materials](ch24_accessible_docs.md)
- [Chapter 25: Checklists and Templates](../part5/ch25_checklists_templates.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
