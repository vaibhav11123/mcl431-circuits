# Draw a sequence

Tools: `list_symbols`, `validate_spec`, `eval_spec`, `draw_spec`, `get_sheet`.

Never invent ids. Never generate an image. If chat has no picture, call `get_sheet` with the same YAML.

Recovery:
- `.ct` / FluidSIM: We do not export FluidSIM. Download SVG, PDF, and YAML.
- simulate pressure: No pressure physics. Open the sequence explorer.
- cascade >3 cylinders: Cascade for more than three cylinders is not in this pack. Here is the electropneumatic 5/2 equivalent.
- unknown valve: list_symbols ids
- missing valve type: draw 5/2, assumption on the report
- photograph: We cannot verify a photograph. Type the sequence or paste YAML.
