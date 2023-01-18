

def generate_dc_code(dc):
    code = list()
    code.append("from dataclasses import dataclass, field")
    code.append("")
    code.append("@dataclass")
    