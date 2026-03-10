from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml


FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


@dataclass
class SkillRecord:
    name: str
    description: str
    path: str


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1)) or {}
    return {str(key): str(value) for key, value in data.items()}


def scan_skills(base_dir: Path) -> list[SkillRecord]:
    skills_dir = base_dir / "skills"
    records: list[SkillRecord] = []
    if not skills_dir.exists():
        return records

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        records.append(
            SkillRecord(
                name=meta.get("name", skill_file.parent.name),
                description=meta.get("description", "No description"),
                path=str(skill_file.relative_to(base_dir)).replace("\\", "/"),
            )
        )
    return records


def build_snapshot(skills: list[SkillRecord]) -> str:
    lines = [
        "<skills>",
        "  <summary>Available local skills that the agent can inspect with read_file.</summary>",
    ]
    for skill in skills:
        lines.extend(
            [
                f'  <skill name="{skill.name}" path="{skill.path}">',
                f"    <description>{skill.description}</description>",
                "  </skill>",
            ]
        )
    lines.append("</skills>")
    return "\n".join(lines) + "\n"


def refresh_snapshot(base_dir: Path) -> Path:
    snapshot_path = base_dir / "SKILLS_SNAPSHOT.md"
    snapshot_path.write_text(
        build_snapshot(scan_skills(base_dir)),
        encoding="utf-8",
    )
    return snapshot_path
