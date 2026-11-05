from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT_DIR = Path("artifacts")
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "pytorch_learning_packet.docx"

NAVY = "17365D"
BLUE = "2F5597"
PALE_BLUE = "EAF2F8"
PALE_GRAY = "F3F4F6"
MID_GRAY = "D9D9D9"
DARK_GRAY = "404040"
WHITE = "FFFFFF"
BLACK = "000000"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=MID_GRAY, size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_row_cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def set_run_font(run, name, size=None, bold=None, color=None, italic=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), name)
    rpr.rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    if italic is not None:
        run.italic = italic


def set_para_shading(paragraph, fill):
    p_pr = paragraph._p.get_or_add_pPr()
    shd = p_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        p_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_run_font(run, "Liberation Sans", 8.5, color="666666")
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    header = table.rows[0]
    set_repeat_table_header(header)
    set_row_cant_split(header)
    for idx, text in enumerate(headers):
        cell = header.cells[idx]
        set_cell_shading(cell, NAVY)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        set_run_font(r, "Liberation Sans", 9.2, bold=True, color=WHITE)
        if widths:
            cell.width = Inches(widths[idx])
    for r_idx, row_data in enumerate(rows):
        cells = table.add_row().cells
        set_row_cant_split(table.rows[-1])
        for c_idx, text in enumerate(row_data):
            cell = cells[c_idx]
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if r_idx % 2 == 1:
                set_cell_shading(cell, PALE_BLUE)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(text))
            set_run_font(run, "Liberation Sans", 9.1, color=BLACK)
            if widths:
                cell.width = Inches(widths[c_idx])
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(0)
    return table


def add_code(doc, code):
    p = doc.add_paragraph(style="Code")
    set_para_shading(p, PALE_GRAY)
    lines = code.strip("\n").splitlines()
    for idx, line in enumerate(lines):
        r = p.add_run(line)
        set_run_font(r, "Liberation Mono", 8.7, color=BLACK)
        if idx < len(lines) - 1:
            r.add_break()
    return p


def add_bullets(doc, items, level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.left_indent = Inches(0.25 + 0.25 * level)
        p.paragraph_format.first_line_indent = Inches(-0.15)
        p.add_run(item)


def add_numbered(doc, items):
    for index, item in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.22)
        p.paragraph_format.first_line_indent = Inches(-0.22)
        p.paragraph_format.space_after = Pt(3)
        lead = p.add_run(f"{index}.  ")
        set_run_font(lead, "Liberation Sans", 10.5, bold=True, color=BLACK)
        body = p.add_run(item)
        set_run_font(body, "Liberation Sans", 10.5, color=BLACK)


def add_exercise(doc, number, title, prompt, response_lines=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"Exercise {number}  {title}")
    set_run_font(r, "Liberation Sans", 11, bold=True, color=BLACK)
    p2 = doc.add_paragraph(prompt)
    p2.paragraph_format.space_after = Pt(3)
    for _ in range(response_lines):
        line = doc.add_paragraph("________________________________________________________________________________")
        line.paragraph_format.space_after = Pt(2)
        for run in line.runs:
            set_run_font(run, "Liberation Sans", 8, color="A6A6A6")


def add_tip(doc, label, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(6)
    lead = p.add_run(f"{label}: ")
    set_run_font(lead, "Liberation Sans", 10.5, bold=True, color=BLACK)
    body = p.add_run(text)
    set_run_font(body, "Liberation Sans", 10.5, color=BLACK)


def add_module_header(doc, number, title, time, outcome):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(f"MODULE {number}")
    set_run_font(r, "Liberation Sans", 9, bold=True, color=BLUE)
    doc.add_heading(title, level=1)
    meta = doc.add_paragraph()
    meta.paragraph_format.space_after = Pt(10)
    r1 = meta.add_run(f"Suggested time  {time}   |   Outcome  ")
    set_run_font(r1, "Liberation Sans", 9.5, bold=True, color=DARK_GRAY)
    r2 = meta.add_run(outcome)
    set_run_font(r2, "Liberation Sans", 9.5, color=DARK_GRAY)


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(0.72)
section.bottom_margin = Inches(0.68)
section.left_margin = Inches(0.82)
section.right_margin = Inches(0.82)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Liberation Sans"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Liberation Sans")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Liberation Sans")
normal.font.size = Pt(10.5)
normal.font.color.rgb = RGBColor.from_string(BLACK)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.08

title_style = styles["Title"]
title_style.font.name = "Liberation Sans"
title_style._element.rPr.rFonts.set(qn("w:ascii"), "Liberation Sans")
title_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Liberation Sans")
title_style.font.size = Pt(30)
title_style.font.bold = True
title_style.font.color.rgb = RGBColor.from_string(BLACK)
title_ppr = title_style.element.get_or_add_pPr()
title_border = title_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_ppr.remove(title_border)

for name, size, before, after in (
    ("Heading 1", 20, 8, 8),
    ("Heading 2", 14, 10, 5),
    ("Heading 3", 11.5, 8, 4),
):
    s = styles[name]
    s.font.name = "Liberation Sans"
    s._element.rPr.rFonts.set(qn("w:ascii"), "Liberation Sans")
    s._element.rPr.rFonts.set(qn("w:hAnsi"), "Liberation Sans")
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = RGBColor.from_string(BLACK)
    s.paragraph_format.space_before = Pt(before)
    s.paragraph_format.space_after = Pt(after)
    s.paragraph_format.keep_with_next = True

code_style = styles.add_style("Code", 1)
code_style.font.name = "Liberation Mono"
code_style._element.rPr.rFonts.set(qn("w:ascii"), "Liberation Mono")
code_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Liberation Mono")
code_style.font.size = Pt(8.7)
code_style.paragraph_format.left_indent = Inches(0.18)
code_style.paragraph_format.right_indent = Inches(0.18)
code_style.paragraph_format.space_before = Pt(4)
code_style.paragraph_format.space_after = Pt(7)
code_style.paragraph_format.line_spacing = 1.0

for list_name in ("List Bullet", "List Bullet 2", "List Number"):
    styles[list_name].font.name = "Liberation Sans"
    styles[list_name]._element.rPr.rFonts.set(qn("w:ascii"), "Liberation Sans")
    styles[list_name]._element.rPr.rFonts.set(qn("w:hAnsi"), "Liberation Sans")
    styles[list_name].font.size = Pt(10.5)
    styles[list_name].paragraph_format.space_after = Pt(3)

header_p = section.header.paragraphs[0]
header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = header_p.add_run("PYTORCH LEARNING PACKET")
set_run_font(hr, "Liberation Sans", 8, bold=True, color="777777")
add_page_number(section.footer.paragraphs[0])

# Cover
p = doc.add_paragraph("SELF PACED STUDY GUIDE")
p.paragraph_format.space_before = Pt(60)
p.paragraph_format.space_after = Pt(12)
set_run_font(p.runs[0], "Liberation Sans", 10, bold=True, color=BLUE)
doc.add_paragraph("PyTorch Learning Packet", style="Title")
subtitle = doc.add_paragraph(
    "A practical introduction to tensors, gradients, data pipelines, neural networks, training, and model persistence"
)
subtitle.paragraph_format.space_before = Pt(8)
subtitle.paragraph_format.space_after = Pt(24)
for r in subtitle.runs:
    set_run_font(r, "Liberation Sans", 15, color=DARK_GRAY)

intro = doc.add_paragraph(
    "This packet teaches the core PyTorch workflow by building ideas in the same order that a model uses them: represent data, define computation, calculate gradients, update parameters, evaluate behavior, and save what you learned. By the end, you will be able to train and troubleshoot a small classifier without relying on copied boilerplate."
)
intro.paragraph_format.space_after = Pt(18)
for r in intro.runs:
    set_run_font(r, "Liberation Sans", 11.5, color=BLACK)

add_table(
    doc,
    ["Best for", "Time", "Prerequisites", "You will produce"],
    [["Beginners with basic Python", "6 to 8 hours", "Functions, loops, classes, basic algebra", "A trained two class neural network"]],
    [1.7, 1.0, 2.2, 1.75],
)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(16)
p.add_run("Name  ").bold = True
p.add_run("____________________________________")
p = doc.add_paragraph()
p.add_run("Start date  ").bold = True
p.add_run("__________________   ")
p.add_run("Target finish  ").bold = True
p.add_run("__________________")

doc.add_page_break()
doc.add_heading("How to use this packet", level=1)
doc.add_paragraph(
    "Work through the modules in order if PyTorch is new to you. Type every code sample instead of pasting it, predict the result before running it, and record what changed when your prediction was wrong. The exercises are intentionally short; the mini project combines them into a complete workflow. Answers appear near the end."
)
add_numbered(doc, [
    "Read the concept and inspect the tensor shapes shown in each example.",
    "Run the example in a notebook or Python file and explain the result aloud.",
    "Complete the practice prompt before looking at the answer key.",
    "Use the debugging guide whenever an error appears; errors are part of the learning path.",
])

doc.add_heading("Learning outcomes", level=2)
add_bullets(doc, [
    "Create tensors with deliberate shapes, data types, and devices.",
    "Explain how automatic differentiation connects a loss to parameter updates.",
    "Build Dataset and DataLoader pipelines for batching and shuffling.",
    "Define an nn.Module and reason about the input and output of each layer.",
    "Write separate training and evaluation loops.",
    "Save model weights and restore them safely for inference.",
    "Diagnose common shape, dtype, device, gradient, and mode errors.",
])

doc.add_heading("Packet map", level=2)
add_table(
    doc,
    ["Module", "Focus", "Checkpoint"],
    [
        ["1", "Tensors and devices", "Manipulate a batch without losing shape"],
        ["2", "Autograd", "Compute and reset gradients"],
        ["3", "Data pipelines", "Inspect batches from a DataLoader"],
        ["4", "Models and loss", "Trace shapes through an nn.Module"],
        ["5", "Training and evaluation", "Train without leaking gradients into evaluation"],
        ["6", "Persistence and next steps", "Save, restore, and run inference"],
    ],
    [0.75, 2.15, 3.75],
)

doc.add_heading("The machine learning loop in one minute", level=2)
doc.add_paragraph(
    "A model turns inputs into predictions. A loss function measures how wrong the predictions are. Autograd calculates how each trainable parameter contributed to that loss. An optimizer uses those gradients to adjust the parameters. Repeating this sequence over batches is training. Evaluation runs the model on held-out data without updating parameters."
)
add_code(doc, """predictions = model(inputs)
loss = loss_fn(predictions, targets)
optimizer.zero_grad()
loss.backward()
optimizer.step()""")
add_tip(doc, "Core question", "At every line, ask: what is the tensor shape, dtype, device, and role?")

doc.add_page_break()
doc.add_heading("Set up your environment", level=1)
doc.add_paragraph(
    "Use the installation selector on the official PyTorch website because the correct command depends on your operating system and accelerator. A CPU installation is sufficient for every activity in this packet. After installation, verify the library and select an available device."
)
add_code(doc, """import torch

print(torch.__version__)

device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {device}")

torch.manual_seed(7)""")
add_tip(doc, "Expected result", "You should see a version string and one of cpu, cuda, or mps. The examples work on all three.")
doc.add_heading("Suggested workspace", level=2)
add_bullets(doc, [
    "Notebook option: one notebook with a heading for each module.",
    "Script option: one folder with practice.py, train.py, and artifacts for saved weights.",
    "Keep experiments small until the training loop is correct. Faster feedback beats a larger model.",
])
doc.add_heading("Quick readiness check", level=2)
add_code(doc, """x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], device=device)
print(x.shape, x.dtype, x.device)
print(x @ x)""")
add_exercise(doc, "0", "Read the output", "Write the shape, dtype, and device of x. Then calculate the top left value of x @ x by hand.", 3)

add_module_header(doc, "1", "Tensors and devices", "60 to 75 minutes", "Use shapes, dtypes, indexing, and broadcasting deliberately")
doc.add_paragraph(
    "A tensor is an n dimensional array that can run on accelerators and participate in automatic differentiation. Most PyTorch bugs begin as a mismatch in shape, dtype, or device, so inspect those three properties early and often."
)
doc.add_heading("Read a tensor as data plus metadata", level=2)
add_code(doc, """x = torch.tensor(
    [[1, 2, 3], [4, 5, 6]],
    dtype=torch.float32,
    device=device,
)

print(x.shape)   # torch.Size([2, 3])
print(x.dtype)   # torch.float32
print(x.device)
print(x.ndim)    # 2""")
add_table(
    doc,
    ["Property", "Question it answers", "Example"],
    [
        ["shape", "How many items exist along each axis?", "[batch, features]"],
        ["dtype", "What kind of values are stored?", "float32 or int64"],
        ["device", "Where is the tensor stored and computed?", "cpu, cuda, or mps"],
        ["requires_grad", "Should autograd track operations on it?", "Usually true for parameters"],
    ],
    [1.2, 3.25, 2.2],
)
doc.add_heading("Create and reshape", level=2)
add_code(doc, """a = torch.arange(12, dtype=torch.float32).reshape(3, 4)
row_means = a.mean(dim=1)
column_sums = a.sum(dim=0)
flat = a.flatten()

print(a)
print(row_means.shape)   # [3]
print(column_sums.shape) # [4]
print(flat.shape)        # [12]""")
add_tip(doc, "Shape habit", "Write the expected shape beside every important operation before running it.")

doc.add_heading("Indexing and slicing", level=2)
add_code(doc, """batch = torch.randn(8, 3, 32, 32)  # N, C, H, W
first_image = batch[0]                 # [3, 32, 32]
red_channel = batch[:, 0]              # [8, 32, 32]
center_crop = batch[:, :, 8:24, 8:24]  # [8, 3, 16, 16]""")
doc.add_heading("Broadcasting", level=2)
doc.add_paragraph(
    "Broadcasting lets PyTorch combine tensors whose shapes are compatible. Dimensions are compared from the right. Two dimensions are compatible when they are equal or one of them is 1. Broadcasting is convenient, but an accidental singleton dimension can silently produce the wrong result."
)
add_code(doc, """scores = torch.randn(4, 3)        # four samples, three classes
bias = torch.tensor([0.1, 0.0, -0.1])
adjusted = scores + bias             # bias broadcasts to [4, 3]""")
add_exercise(doc, "1.1", "Shape tracing", "For a tensor shaped [32, 10], what are the shapes of x.mean(dim=0), x.mean(dim=1), and x[:, :3]?", 3)
add_exercise(doc, "1.2", "Normalize features", "Write one line that centers a [batch, features] tensor by subtracting the mean of each feature. Keep the feature mean compatible with broadcasting.", 3)

doc.add_heading("Tensor practice lab", level=1)
doc.add_paragraph("Run this starter code, then complete the tasks without converting tensors to Python lists or NumPy arrays.")
add_code(doc, """torch.manual_seed(7)
x = torch.randn(6, 4)

# A. Select the last two columns.
# B. Compute one mean for each row.
# C. Standardize each column using its mean and standard deviation.
# D. Confirm that the standardized column means are near zero.""")
add_exercise(doc, "1.3", "Explain your result", "Why should the standardized column means be near zero rather than exactly zero? What shape should the means have?", 4)
doc.add_heading("Checkpoint", level=2)
add_bullets(doc, [
    "I can distinguish a scalar, vector, matrix, and higher dimensional tensor.",
    "I can predict the output shape of indexing and reduction operations.",
    "I can move data and a model to the same device.",
    "I can explain when broadcasting will and will not work.",
])

add_module_header(doc, "2", "Automatic differentiation", "50 to 60 minutes", "Connect a loss value to parameter gradients")
doc.add_paragraph(
    "Automatic differentiation records tensor operations in a computation graph. When you call backward on a scalar result, PyTorch follows the graph backward and stores derivatives in the .grad fields of leaf tensors that require gradients."
)
doc.add_heading("A single parameter", level=2)
add_code(doc, """w = torch.tensor(2.0, requires_grad=True)
x = torch.tensor(3.0)
target = torch.tensor(10.0)

prediction = w * x
loss = (prediction - target) ** 2
loss.backward()

print(loss.item())  # 16.0
print(w.grad)        # -24.0""")
doc.add_paragraph(
    "The derivative is negative because increasing w would move the prediction from 6 toward the target 10. The gradient describes a local slope; an optimizer chooses how far to move in the opposite direction."
)
doc.add_heading("Gradients accumulate", level=2)
doc.add_paragraph(
    "Calling backward adds to existing gradients. This behavior enables gradient accumulation across batches, but it also means ordinary training loops must clear gradients before the next backward pass."
)
add_code(doc, """w.grad = None
loss = (w * x - target) ** 2
loss.backward()
print(w.grad)""")
add_tip(doc, "Training convention", "Use optimizer.zero_grad() before loss.backward(). Setting gradients to None is often the efficient default behavior of current optimizers.")
doc.add_heading("Stop tracking when gradients are not needed", level=2)
add_code(doc, """model.eval()
with torch.inference_mode():
    predictions = model(inputs)""")
doc.add_paragraph(
    "Evaluation mode and gradient tracking solve different problems. model.eval() changes the behavior of layers such as dropout and batch normalization. torch.inference_mode() disables gradient recording. Use both for evaluation and inference."
)
add_exercise(doc, "2.1", "Differentiate by hand", "For loss = (w x - y)^2 with w = 1, x = 4, and y = 10, calculate the prediction, loss, and derivative of loss with respect to w.", 2)
add_exercise(doc, "2.2", "Find the bug", "A loop calls loss.backward() and optimizer.step() but never calls optimizer.zero_grad(). Describe what happens and how to fix it.", 1)

add_module_header(doc, "3", "Datasets and DataLoaders", "60 to 75 minutes", "Turn samples into shuffled mini batches")
doc.add_paragraph(
    "A Dataset answers two questions: how many samples exist, and what sample lives at a given index? A DataLoader handles iteration concerns such as batching, shuffling, and optional multiprocessing. Keeping these responsibilities separate makes data pipelines easier to test."
)
doc.add_heading("Start with TensorDataset", level=2)
add_code(doc, """from torch.utils.data import DataLoader, TensorDataset

X = torch.tensor(
    [[-1.0, -1.0], [-0.8, -1.2], [1.0, 1.1], [0.9, 0.7]],
    dtype=torch.float32,
)
y = torch.tensor([0, 0, 1, 1], dtype=torch.long)

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=2, shuffle=True)

for features, labels in loader:
    print(features.shape, labels.shape)""")
add_tip(doc, "Classification dtype", "CrossEntropyLoss expects class-index targets stored as torch.long, not one-hot vectors or floating-point class IDs.")
doc.add_heading("Create a custom Dataset", level=2)
add_code(doc, """from torch.utils.data import Dataset

class PairDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return self.features[index], self.labels[index]""")
doc.add_heading("Train, validation, and test roles", level=2)
add_table(
    doc,
    ["Split", "Used for", "Should update parameters"],
    [
        ["Training", "Fitting model parameters", "Yes"],
        ["Validation", "Choosing settings and monitoring generalization", "No"],
        ["Test", "Final unbiased estimate after choices are complete", "No"],
    ],
    [1.1, 4.3, 1.3],
)
add_exercise(doc, "3.1", "Inspect one batch", "Given 100 samples, batch_size=32, and drop_last=False, how many batches are produced and what is the size of the final batch?", 3)
add_exercise(doc, "3.2", "Choose shuffle settings", "Should a standard training loader shuffle? Should a validation loader shuffle? Explain what each choice changes.", 4)

doc.add_heading("Data pipeline checklist", level=1)
add_bullets(doc, [
    "Inspect one raw sample before batching.",
    "Print one batch of features and labels, including shape and dtype.",
    "Confirm that feature scaling matches what the model expects.",
    "Confirm that targets use the representation expected by the loss function.",
    "Verify that training and evaluation splits do not overlap.",
    "Start with num_workers=0 while debugging, then tune data loading only if needed.",
])
doc.add_heading("Pipeline diagnosis", level=2)
add_table(
    doc,
    ["Symptom", "Likely cause", "First check"],
    [
        ["Size mismatch in loss", "Prediction and target shapes disagree", "Print logits.shape and y.shape"],
        ["Expected Long but found Float", "Class labels have the wrong dtype", "Print y.dtype"],
        ["Training changes every run", "Randomness or nondeterministic operations", "Set seeds and control data shuffling"],
        ["GPU waits for data", "Input pipeline is the bottleneck", "Measure loading time before tuning workers"],
    ],
    [2.0, 2.65, 2.05],
)

add_module_header(doc, "4", "Models, logits, and loss", "75 to 90 minutes", "Define an nn.Module and match its output to a loss function")
doc.add_heading("A small classifier", level=2)
add_code(doc, """from torch import nn

class Classifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
        )

    def forward(self, x):
        return self.network(x)

model = Classifier().to(device)
print(model)""")
doc.add_paragraph(
    "The model accepts two features per sample and returns two logits per sample. A logit is an unnormalized score. CrossEntropyLoss expects logits directly and internally applies the appropriate log-softmax calculation, so do not add softmax before the loss."
)
doc.add_heading("Trace the shapes", level=2)
add_table(
    doc,
    ["Stage", "Input shape", "Output shape"],
    [
        ["Batch", "[B, 2]", "[B, 2]"],
        ["Linear 2 to 32", "[B, 2]", "[B, 32]"],
        ["ReLU", "[B, 32]", "[B, 32]"],
        ["Linear 32 to 2", "[B, 32]", "[B, 2] logits"],
    ],
    [2.0, 2.1, 2.6],
)
doc.add_heading("Match tasks to outputs and losses", level=2)
add_table(
    doc,
    ["Task", "Model output", "Common loss", "Target"],
    [
        ["Multiclass classification", "[B, C] logits", "CrossEntropyLoss", "[B] long class indices"],
        ["Binary classification", "[B] or [B, 1] logits", "BCEWithLogitsLoss", "Matching float tensor"],
        ["Regression", "[B, K] values", "MSELoss or L1Loss", "Matching float tensor"],
    ],
    [1.75, 1.6, 1.65, 1.7],
)
doc.add_heading("Count trainable parameters", level=2)
add_code(doc, """trainable = sum(
    p.numel() for p in model.parameters() if p.requires_grad
)
print(trainable)""")
add_exercise(doc, "4.1", "Parameter count", "How many trainable parameters are in Linear(2, 32)? Include both weights and bias. Then count Linear(32, 2) and the whole model.", 4)
add_exercise(doc, "4.2", "Repair the loss input", "A student applies softmax to the model output and then passes it to CrossEntropyLoss. Rewrite the two lines correctly and explain why.", 4)

add_module_header(doc, "5", "Training and evaluation", "90 minutes", "Write a correct optimization loop and measure held-out accuracy")
doc.add_heading("Training function", level=2)
add_code(doc, """def train_one_epoch(model, loader, loss_fn, optimizer, device):
    model.train()
    total_loss = 0.0

    for X, y in loader:
        X, y = X.to(device), y.to(device)

        optimizer.zero_grad()
        logits = model(X)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * X.size(0)

    return total_loss / len(loader.dataset)""")
doc.add_heading("Evaluation function", level=2)
add_code(doc, """def evaluate(model, loader, loss_fn, device):
    model.eval()
    total_loss = 0.0
    correct = 0

    with torch.inference_mode():
        for X, y in loader:
            X, y = X.to(device), y.to(device)
            logits = model(X)
            loss = loss_fn(logits, y)

            total_loss += loss.item() * X.size(0)
            correct += (logits.argmax(dim=1) == y).sum().item()

    n = len(loader.dataset)
    return total_loss / n, correct / n""")
doc.add_heading("Run epochs", level=2)
add_code(doc, """loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)

for epoch in range(1, 21):
    train_loss = train_one_epoch(
        model, train_loader, loss_fn, optimizer, device
    )
    val_loss, val_acc = evaluate(
        model, val_loader, loss_fn, device
    )
    print(
        f"epoch={epoch:02d} train_loss={train_loss:.4f} "
        f"val_loss={val_loss:.4f} val_acc={val_acc:.3f}"
    )""")
doc.add_heading("Interpret the curves", level=2)
add_table(
    doc,
    ["Pattern", "Possible interpretation", "Useful response"],
    [
        ["Both losses stay flat", "Learning rate, gradients, data, or labels may be wrong", "Inspect one batch and gradient norms"],
        ["Training improves, validation worsens", "Overfitting", "Use more data, regularization, or fewer epochs"],
        ["Loss becomes NaN", "Unstable updates or invalid data", "Lower learning rate and inspect finite values"],
        ["Accuracy is high but loss is high", "Some predictions may be confidently wrong", "Inspect probabilities and class balance"],
    ],
    [1.8, 3.0, 1.9],
)
add_exercise(doc, "5.1", "Order the steps", "Put these in a valid order: optimizer.step, loss.backward, model(X), optimizer.zero_grad, loss_fn(logits, y).", 3)
add_exercise(doc, "5.2", "Explain evaluation", "Why should evaluation use both model.eval() and torch.inference_mode()?", 4)

doc.add_page_break()
doc.add_heading("Mini project  Classify two clusters", level=1)
doc.add_paragraph(
    "Build a complete classifier using only PyTorch. The data contains two noisy clusters. Your goal is at least 90 percent validation accuracy, but the real objective is a trustworthy workflow."
)
doc.add_heading("1  Generate and split data", level=2)
add_code(doc, """torch.manual_seed(7)
n = 600

class0 = torch.randn(n // 2, 2) * 0.8 + torch.tensor([-1.5, -1.0])
class1 = torch.randn(n // 2, 2) * 0.8 + torch.tensor([1.5, 1.0])
X = torch.cat([class0, class1])
y = torch.cat([
    torch.zeros(n // 2, dtype=torch.long),
    torch.ones(n // 2, dtype=torch.long),
])

order = torch.randperm(n)
X, y = X[order], y[order]
split = int(0.8 * n)
X_train, X_val = X[:split], X[split:]
y_train, y_val = y[:split], y[split:]""")
doc.add_heading("2  Build loaders", level=2)
add_code(doc, """train_loader = DataLoader(
    TensorDataset(X_train, y_train), batch_size=32, shuffle=True
)
val_loader = DataLoader(
    TensorDataset(X_val, y_val), batch_size=64, shuffle=False
)""")
doc.add_heading("3  Complete the workflow", level=2)
add_numbered(doc, [
    "Instantiate Classifier and move it to device.",
    "Create CrossEntropyLoss and an optimizer.",
    "Train for 20 epochs using the provided functions.",
    "Record final training loss, validation loss, and validation accuracy.",
    "Inspect five validation predictions and compare them with the labels.",
    "Change one factor such as hidden width, learning rate, or optimizer. State your hypothesis before rerunning.",
])
doc.add_heading("Experiment record", level=2)
add_table(
    doc,
    ["Run", "Change", "Hypothesis", "Val accuracy", "What I learned"],
    [
        ["1", "Baseline", "", "", ""],
        ["2", "", "", "", ""],
        ["3", "", "", "", ""],
    ],
    [0.55, 1.25, 2.05, 1.0, 1.85],
)
doc.add_heading("Reflection", level=2)
add_exercise(doc, "P.1", "Evidence", "What evidence tells you that learning occurred? Include at least two measurements or observations.", 2)
add_exercise(doc, "P.2", "Limitations", "Why does strong validation accuracy on this simple dataset not prove that the model will work on unrelated data?", 2)

add_module_header(doc, "6", "Save, load, and extend", "45 to 60 minutes", "Restore trained weights and run inference correctly")
doc.add_heading("Save weights", level=2)
add_code(doc, """torch.save(model.state_dict(), "cluster_classifier.pt")""")
doc.add_heading("Restore weights", level=2)
add_code(doc, """restored = Classifier().to(device)
state = torch.load(
    "cluster_classifier.pt",
    map_location=device,
    weights_only=True,
)
restored.load_state_dict(state)
restored.eval()""")
doc.add_paragraph(
    "The architecture must match the saved state dictionary. Saving a state dictionary is the standard portable pattern. Loading weights with weights_only=True reduces the amount of executable content accepted during deserialization, but you should still treat model files from unknown sources as untrusted."
)
doc.add_heading("Run one prediction", level=2)
add_code(doc, """sample = torch.tensor(
    [[0.5, 1.0]], dtype=torch.float32, device=device
)
with torch.inference_mode():
    logits = restored(sample)
    probability = logits.softmax(dim=1)
    predicted_class = probability.argmax(dim=1)

print(probability.cpu(), predicted_class.item())""")
doc.add_heading("Save a resumable checkpoint", level=2)
add_code(doc, """torch.save(
    {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "validation_accuracy": val_acc,
    },
    "checkpoint.pt",
)""")
add_tip(doc, "Design principle", "Save the information needed for the task: weights for inference, or a checkpoint with optimizer and epoch state to resume training.")
doc.add_heading("Optional performance extension", level=2)
doc.add_paragraph(
    "After your eager model is correct and measured, you can experiment with torch.compile on supported environments. Compilation may improve performance, but it introduces compilation overhead and can require debugging graph breaks. Benchmark the workload that matters rather than assuming a speedup."
)
add_code(doc, """compiled_model = torch.compile(model)""")
add_exercise(doc, "6.1", "Persistence plan", "For each scenario, choose weights only or a resumable checkpoint: shipping inference, pausing training overnight, and sharing a model architecture plus learned parameters.", 2)

doc.add_heading("Debugging guide", level=1)
doc.add_paragraph(
    "Debug from the outside inward. Confirm the data first, then a forward pass, then the loss, then gradients, then updates. Changing the architecture before validating these basics often hides the actual problem."
)
add_numbered(doc, [
    "Reduce to one batch and print shapes, dtypes, devices, minimums, and maximums.",
    "Run logits = model(X) and inspect its shape and finite values.",
    "Compute the loss and confirm it is a finite scalar.",
    "Call backward once and inspect whether representative parameter gradients exist and are finite.",
    "Take one optimizer step and confirm that at least one parameter changed.",
    "Try to overfit a tiny subset. Failure to do so often signals a pipeline or optimization bug.",
])
doc.add_heading("Common errors", level=2)
add_table(
    doc,
    ["Message or symptom", "Meaning", "Correction"],
    [
        ["mat1 and mat2 shapes cannot be multiplied", "A Linear layer received the wrong final dimension", "Print X.shape before the layer and fix features or in_features"],
        ["Expected all tensors to be on the same device", "Model and data are on different devices", "Move both model and every batch to device"],
        ["Target out of bounds", "A class index is outside 0 through C minus 1", "Inspect unique labels and number of logits"],
        ["element does not require grad", "The graph was detached or gradients were disabled", "Inspect requires_grad and surrounding contexts"],
        ["Validation changes between identical calls", "Model may still be in training mode", "Call model.eval and check stochastic preprocessing"],
        ["Loss falls but metric is wrong", "Metric logic, target mapping, or imbalance may mislead", "Inspect examples and calculate a confusion matrix"],
    ],
    [2.25, 2.4, 2.05],
)
doc.add_heading("Gradient inspection", level=2)
add_code(doc, """for name, parameter in model.named_parameters():
    if parameter.grad is not None:
        print(name, parameter.grad.norm().item())""")
add_tip(doc, "Interpret cautiously", "A zero, tiny, or large gradient can be meaningful. Look for persistent patterns across layers and steps, not a single magic threshold.")

doc.add_page_break()
doc.add_heading("Knowledge check", level=1)
questions = [
    "What four properties should you inspect when a tensor-related error occurs?",
    "Why does CrossEntropyLoss usually receive logits rather than softmax probabilities?",
    "What is the difference between model.train() and enabling gradients?",
    "Why are gradients cleared in a standard training loop?",
    "What does DataLoader add on top of Dataset?",
    "Why should validation data not update model parameters?",
    "What does logits.argmax(dim=1) return for a [B, C] tensor?",
    "Why must the model architecture be recreated before loading a state dictionary?",
    "What does it mean to overfit a tiny batch, and why is that a useful test?",
    "Name one reason validation loss can rise while training loss falls.",
]
for i, q in enumerate(questions, 1):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"{i}. {q}")
    set_run_font(r, "Liberation Sans", 10.5, bold=True, color=BLACK)
    for _ in range(2):
        line = doc.add_paragraph("________________________________________________________________________________")
        line.paragraph_format.space_after = Pt(2)
        for run in line.runs:
            set_run_font(run, "Liberation Sans", 8, color="A6A6A6")

doc.add_page_break()
doc.add_heading("Answer key", level=1)
doc.add_heading("Exercises", level=2)
answers = [
    ("0", "x has shape [2, 2], dtype float32, and the selected device. The top left entry of x @ x is 1 x 1 + 2 x 3 = 7."),
    ("1.1", "x.mean(dim=0) has shape [10], x.mean(dim=1) has shape [32], and x[:, :3] has shape [32, 3]."),
    ("1.2", "x - x.mean(dim=0, keepdim=True). keepdim=True produces shape [1, features], which broadcasts across the batch."),
    ("1.3", "Floating-point arithmetic has finite precision, so results can have small rounding error. The column means have shape [4]."),
    ("2.1", "Prediction = 4. Loss = 36. The derivative is 2(wx - y)x = 2(4 - 10)4 = -48."),
    ("2.2", "Each backward call adds new gradients to old ones, so updates use accumulated gradients unintentionally. Call optimizer.zero_grad() before backward."),
    ("3.1", "Four batches are produced. The first three contain 32 samples and the final batch contains 4."),
    ("3.2", "Training normally shuffles to vary batch composition and reduce ordering effects. Validation normally does not need shuffling because parameters are not updated; fixed order also aids reproducibility and example-level inspection."),
    ("4.1", "Linear(2, 32) has 2 x 32 weights plus 32 biases = 96. Linear(32, 2) has 64 weights plus 2 biases = 66. Total = 162."),
    ("4.2", "Use logits = model(X) followed by loss = loss_fn(logits, y). CrossEntropyLoss expects raw logits and applies the numerically stable transformation internally."),
    ("5.1", "optimizer.zero_grad(), logits = model(X), loss = loss_fn(logits, y), loss.backward(), optimizer.step()."),
    ("5.2", "model.eval() changes evaluation-sensitive layers. inference_mode disables gradient recording and reduces overhead. One does not replace the other."),
    ("6.1", "Shipping inference: weights only. Pausing training: resumable checkpoint. Sharing architecture plus learned parameters: source or configuration for the architecture plus weights only."),
    ("P.1", "Strong evidence could include decreasing training loss, good held-out accuracy, correct example-level predictions, and performance better than a simple baseline."),
    ("P.2", "The validation set comes from the same simple data-generating process. Unrelated data can differ in features, labels, noise, class balance, or meaning, so the result does not establish broad generalization."),
]
for label, answer in answers:
    p = doc.add_paragraph()
    r = p.add_run(f"{label}  ")
    set_run_font(r, "Liberation Sans", 10.2, bold=True, color=BLACK)
    r2 = p.add_run(answer)
    set_run_font(r2, "Liberation Sans", 10.2, color=BLACK)

doc.add_heading("Knowledge check", level=2)
knowledge_answers = [
    "Shape, dtype, device, and whether gradients are required or available.",
    "The loss performs the stable log-softmax calculation internally; pre-applying softmax changes the expected input and can weaken numerical behavior.",
    "model.train() sets layer behavior. Gradient recording is controlled by requires_grad and gradient-mode contexts.",
    "Gradients accumulate by design; clearing prevents unintended carryover from earlier batches.",
    "Batching, iteration, shuffling, sampling, collation, and optional worker processes.",
    "Validation estimates behavior on held-out data. Updating on it would leak information and bias that estimate.",
    "The index of the largest logit for each sample, producing shape [B].",
    "A state dictionary stores named tensors, not the Python code that defines how the model connects them.",
    "It means fitting a very small sample nearly perfectly. If the model cannot do this, the training pipeline may be broken or capacity may be insufficient.",
    "Overfitting: the model continues fitting training-specific patterns that do not generalize.",
]
for idx, answer in enumerate(knowledge_answers, 1):
    p = doc.add_paragraph()
    p.add_run(f"{idx}. ").bold = True
    p.add_run(answer)

doc.add_heading("PyTorch quick reference", level=1)
add_table(
    doc,
    ["Goal", "Pattern"],
    [
        ["Create float tensor", "torch.tensor(data, dtype=torch.float32)"],
        ["Inspect", "x.shape, x.dtype, x.device, x.requires_grad"],
        ["Move", "x = x.to(device); model = model.to(device)"],
        ["Reshape", "x.reshape(...), x.flatten(start_dim=1)"],
        ["Batch data", "DataLoader(dataset, batch_size=32, shuffle=True)"],
        ["Define model", "class Model(nn.Module) with forward(self, x)"],
        ["Train mode", "model.train()"],
        ["Evaluation mode", "model.eval() with torch.inference_mode()"],
        ["Clear gradients", "optimizer.zero_grad()"],
        ["Backpropagate", "loss.backward()"],
        ["Update", "optimizer.step()"],
        ["Predict class", "logits.argmax(dim=1)"],
        ["Save weights", "torch.save(model.state_dict(), path)"],
        ["Load weights", "model.load_state_dict(torch.load(path, weights_only=True))"],
    ],
    [2.0, 4.7],
)
doc.add_heading("A reliable loop template", level=2)
add_code(doc, """for X, y in train_loader:
    X, y = X.to(device), y.to(device)
    optimizer.zero_grad()
    logits = model(X)
    loss = loss_fn(logits, y)
    loss.backward()
    optimizer.step()""")
doc.add_heading("Next learning steps", level=2)
add_bullets(doc, [
    "Convolutional neural networks and image tensors.",
    "Embeddings, attention, and sequence models.",
    "Learning-rate schedules, regularization, and experiment tracking.",
    "Mixed precision and performance profiling on supported accelerators.",
    "torch.compile after correctness and measurement are established.",
])

doc.add_heading("Official references", level=1)
doc.add_paragraph(
    "These references were used to align the packet with the current PyTorch learning path and recommended API patterns. Because installation commands and some APIs evolve, check the official documentation when moving the examples into a new environment."
)
refs = [
    ("Learn the Basics", "https://docs.pytorch.org/tutorials/beginner/basics/intro.html"),
    ("Quickstart", "https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html"),
    ("Tensors", "https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html"),
    ("Datasets and DataLoaders", "https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html"),
    ("Automatic differentiation", "https://docs.pytorch.org/tutorials/beginner/basics/autograd_tutorial.html"),
    ("Optimization loop", "https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html"),
    ("Save and load models", "https://docs.pytorch.org/tutorials/beginner/basics/saveloadrun_tutorial.html"),
    ("torch.compile API", "https://docs.pytorch.org/docs/stable/generated/torch.compile.html"),
    ("Installation selector", "https://pytorch.org/get-started/locally/"),
]
for title, url in refs:
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(f"{title}: {url}")
    set_run_font(r, "Liberation Sans", 10, color=BLACK)

doc.add_heading("Completion record", level=2)
add_table(
    doc,
    ["Milestone", "Complete", "Notes"],
    [
        ["Modules 1 through 3", "[  ]", ""],
        ["Modules 4 through 6", "[  ]", ""],
        ["Mini project", "[  ]", ""],
        ["Knowledge check", "[  ]", ""],
        ["Next step selected", "[  ]", ""],
    ],
    [2.25, 1.0, 3.45],
)

props = doc.core_properties
props.title = "PyTorch Learning Packet"
props.subject = "Beginner learning packet for PyTorch"
props.author = ""
props.keywords = "PyTorch, tensors, autograd, DataLoader, neural network, training"

doc.save(OUT_PATH)
print(OUT_PATH.resolve())
