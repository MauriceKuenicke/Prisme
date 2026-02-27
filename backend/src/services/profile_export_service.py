"""Profile PDF export service using ReportLab."""

import io
import json
import re
from datetime import datetime, timezone
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FILENAME_ALLOWED_RE = re.compile(r"[^\w\s\-.]")
WHITESPACE_RE = re.compile(r"[\s]+")
ARETO_PRIMARY_COLOR = "#0E4B8A"
ARETO_SECONDARY_COLOR = "#1AA6B7"
DEFAULT_ACCENT_COLOR = ARETO_PRIMARY_COLOR


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage."""
    cleaned = FILENAME_ALLOWED_RE.sub("", filename.strip())
    cleaned = WHITESPACE_RE.sub("_", cleaned)
    cleaned = cleaned.strip("._-")[:120]
    return cleaned or "consultant_profile"


def escape_xml(text: str) -> str:
    """Escape XML/HTML special characters for use in ReportLab paragraphs."""
    if not text:
        return ""

    text = str(text)
    # Escape XML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text


def parse_hex_color(hex_color: str) -> colors.Color:
    """Convert hex color to ReportLab Color object."""
    if not hex_color:
        return colors.HexColor(DEFAULT_ACCENT_COLOR)

    hex_color = hex_color.strip('#')
    if len(hex_color) != 6:
        return colors.HexColor(DEFAULT_ACCENT_COLOR)

    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
    except ValueError:
        return colors.HexColor(DEFAULT_ACCENT_COLOR)

    return colors.Color(r, g, b)


def parse_list_like(value) -> list[str]:
    """Parse values that may be list, JSON string, or comma-separated text."""
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []

        looks_like_json_array = text.startswith("[") and text.endswith("]")
        if looks_like_json_array:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
            if parsed is not None:
                return []

        if ',' in text:
            return [item.strip() for item in text.split(',') if item.strip()]
        return [text]

    return [str(value).strip()]


def format_display_date(value: Optional[str]) -> Optional[str]:
    """Format dates into a concise readable format."""
    if not value:
        return None

    text = str(value).strip()
    if not text:
        return None

    candidates = [text, text[:10]]
    for candidate in candidates:
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                parsed = datetime.strptime(candidate, fmt)
                if fmt == "%Y":
                    return parsed.strftime("%Y")
                if fmt == "%Y-%m":
                    return parsed.strftime("%b %Y")
                return parsed.strftime("%b %Y")
            except ValueError:
                continue

    return text


def format_multiline_text(value: Optional[str]) -> str:
    """Convert text with line breaks to paragraph-safe markup."""
    if not value:
        return ""
    lines = [escape_xml(line) for line in str(value).splitlines()]
    return "<br/>".join(lines) if lines else ""


class ProfilePDFGenerator:
    """Generate an areto-inspired modern profile PDF from profile data."""

    def __init__(
        self,
        profile_data: dict,
        company_name: Optional[str] = None,
        accent_color: str = "#1A365D",
    ):
        if isinstance(profile_data, str):
            profile_data = json.loads(profile_data)

        self.profile_data = profile_data
        self.company_name = company_name
        resolved_accent = accent_color or ARETO_PRIMARY_COLOR
        self.accent_color = parse_hex_color(resolved_accent)
        self.palette = {
            "brand_primary": colors.HexColor(ARETO_PRIMARY_COLOR),
            "brand_secondary": colors.HexColor(ARETO_SECONDARY_COLOR),
            "text_primary": colors.HexColor("#0F172A"),
            "text_secondary": colors.HexColor("#1E293B"),
            "text_muted": colors.HexColor("#64748B"),
            "surface": colors.HexColor("#F8FBFF"),
            "surface_alt": colors.HexColor("#EEF4FB"),
            "divider": colors.HexColor("#D8E3F0"),
        }

        # Page setup
        self.page_width, self.page_height = A4
        self.margin = 0.82 * inch
        self.content_width = self.page_width - 2 * self.margin

        # Build styles
        self.styles = self._create_styles()

        # Story (content elements)
        self.story = []

    def _create_styles(self):
        """Create custom paragraph styles."""
        styles = StyleSheet1()

        styles.add(ParagraphStyle(
            name='Normal',
            fontName='Helvetica',
            fontSize=10.1,
            leading=14.8,
            textColor=self.palette["text_secondary"],
        ))

        styles.add(ParagraphStyle(
            name='BrandLabel',
            parent=styles['Normal'],
            fontSize=8.7,
            leading=10.2,
            textColor=self.palette["text_muted"],
            fontName='Helvetica-Bold',
            spaceAfter=3,
        ))

        styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=styles['Normal'],
            fontSize=22.5,
            leading=26.2,
            fontName='Helvetica-Bold',
            textColor=self.palette["brand_primary"],
            spaceAfter=1,
        ))

        styles.add(ParagraphStyle(
            name='GeneratedMeta',
            parent=styles['Normal'],
            fontSize=8.7,
            leading=11.2,
            fontName='Helvetica',
            alignment=TA_RIGHT,
            textColor=self.palette["text_muted"],
        ))

        styles.add(ParagraphStyle(
            name='ConsultantName',
            parent=styles['Normal'],
            fontSize=25,
            leading=28.6,
            fontName='Helvetica-Bold',
            textColor=self.palette["text_primary"],
            spaceAfter=2,
        ))

        styles.add(ParagraphStyle(
            name='ConsultantTitle',
            parent=styles['Normal'],
            fontSize=12.2,
            leading=16.8,
            fontName='Helvetica',
            textColor=self.palette["brand_primary"],
            spaceAfter=12,
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Normal'],
            fontSize=10.4,
            leading=13,
            fontName='Helvetica-Bold',
            textColor=self.palette["brand_primary"],
            spaceBefore=20,
            spaceAfter=8,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            name='SectionSubheader',
            parent=styles['Normal'],
            fontSize=9,
            leading=11.2,
            fontName='Helvetica-Bold',
            textColor=self.palette["text_muted"],
            spaceAfter=8,
        ))

        styles.add(ParagraphStyle(
            name='EntryTitle',
            parent=styles['Normal'],
            fontSize=11.5,
            leading=14.6,
            fontName='Helvetica-Bold',
            textColor=self.palette["text_primary"],
            spaceAfter=3,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            name='MetaLine',
            parent=styles['Normal'],
            fontSize=9.2,
            leading=12.8,
            fontName='Helvetica',
            textColor=self.palette["text_muted"],
            spaceAfter=6,
        ))

        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14.6,
            fontName='Helvetica',
            textColor=self.palette["text_secondary"],
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        ))

        styles.add(ParagraphStyle(
            name='DetailLine',
            parent=styles['Normal'],
            fontSize=9.6,
            leading=13.3,
            fontName='Helvetica',
            textColor=self.palette["text_secondary"],
            spaceAfter=5,
        ))

        styles.add(ParagraphStyle(
            name='Quote',
            parent=styles['Normal'],
            fontSize=10.2,
            leading=15.2,
            fontName='Helvetica-Oblique',
            textColor=self.palette["text_secondary"],
            leftIndent=10,
            rightIndent=8,
            spaceAfter=2,
        ))

        styles.add(ParagraphStyle(
            name='FactsLabel',
            parent=styles['Normal'],
            fontSize=8.8,
            leading=11.2,
            fontName='Helvetica-Bold',
            textColor=self.palette["text_muted"],
        ))

        styles.add(ParagraphStyle(
            name='FactsValue',
            parent=styles['Normal'],
            fontSize=9.8,
            leading=13.3,
            fontName='Helvetica',
            textColor=self.palette["text_secondary"],
            alignment=TA_LEFT,
        ))

        styles.add(ParagraphStyle(
            name='SkillSummaryMetric',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=10.6,
            fontName='Helvetica',
            textColor=self.palette["text_secondary"],
            alignment=TA_CENTER,
        ))

        styles.add(ParagraphStyle(
            name='SkillMatrixHeader',
            parent=styles['Normal'],
            fontSize=8.4,
            leading=10,
            fontName='Helvetica-Bold',
            textColor=self.palette["brand_primary"],
            alignment=TA_CENTER,
        ))

        styles.add(ParagraphStyle(
            name='SkillMatrixCell',
            parent=styles['Normal'],
            fontSize=8.2,
            leading=10.2,
            fontName='Helvetica',
            textColor=self.palette["text_secondary"],
        ))

        styles.add(ParagraphStyle(
            name='SkillGridItem',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=10.6,
            fontName='Helvetica',
            textColor=self.palette["text_secondary"],
            alignment=TA_LEFT,
        ))

        return styles

    def _draw_page_chrome(self, canv, doc):
        """Draw page-level header and footer chrome."""
        canv.saveState()

        content_width = self.page_width - doc.leftMargin - doc.rightMargin
        ribbon_y = self.page_height - doc.topMargin + 0.05 * inch
        canv.setFillColor(self.palette["surface_alt"])
        canv.rect(doc.leftMargin, ribbon_y, content_width, 0.22 * inch, stroke=0, fill=1)

        top_line_y = ribbon_y + 0.22 * inch
        canv.setStrokeColor(self.palette["brand_primary"])
        canv.setLineWidth(1.4)
        canv.line(doc.leftMargin, top_line_y, self.page_width - doc.rightMargin, top_line_y)

        footer_line_y = doc.bottomMargin - 0.16 * inch
        canv.setStrokeColor(self.palette["divider"])
        canv.setLineWidth(0.8)
        canv.line(doc.leftMargin, footer_line_y, self.page_width - doc.rightMargin, footer_line_y)

        footer_brand = (self.company_name or "areto group").strip()
        footer_left = f"{footer_brand} | Consultant Profile"

        canv.setFillColor(self.palette["text_muted"])
        canv.setFont("Helvetica", 8.2)
        canv.drawString(doc.leftMargin, doc.bottomMargin - 0.34 * inch, footer_left[:110])
        canv.drawRightString(
            self.page_width - doc.rightMargin,
            doc.bottomMargin - 0.34 * inch,
            f"Confidential | Page {canv.getPageNumber()}",
        )

        canv.restoreState()

    def _add_header(self):
        """Add modern report header with brand and generation metadata."""
        generated_at = self.profile_data.get("generated_at")
        generated_label = "Generated " + datetime.now(timezone.utc).strftime("%b %d, %Y")
        if generated_at:
            formatted_generated = format_display_date(generated_at)
            if formatted_generated:
                generated_label = f"Generated {formatted_generated}"

        consultant = self.profile_data.get("consultant", {})
        consultant_name = f"{consultant.get('first_name', '')} {consultant.get('last_name', '')}".strip()
        brand_label = (self.company_name or "areto group").strip()
        header_left = [
            Paragraph(escape_xml(brand_label.upper()), self.styles["BrandLabel"]),
            Paragraph("Consultant Profile", self.styles["DocumentTitle"]),
        ]
        header_right = [
            Paragraph(escape_xml(generated_label), self.styles["GeneratedMeta"]),
            Paragraph(escape_xml(consultant_name or "Consultant"), self.styles["GeneratedMeta"]),
        ]

        header_table = Table(
            [[header_left, header_right]],
            colWidths=[self.content_width * 0.66, self.content_width * 0.34],
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.75, self.palette["divider"]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        self.story.append(header_table)
        self.story.append(Spacer(1, 0.2 * inch))

    def _add_section_header(self, title: str):
        """Add section heading with separator line."""
        self.story.append(Paragraph(escape_xml(title), self.styles['SectionHeader']))
        self.story.append(HRFlowable(
            width="100%",
            thickness=1.0,
            color=self.palette["brand_secondary"],
            spaceBefore=0,
            spaceAfter=9,
        ))

    def _render_fact_panel(self, facts: list[tuple[str, str]]):
        """Render a clean summary panel for key profile facts."""
        if not facts:
            return

        table_data = [
            [
                Paragraph(escape_xml(label), self.styles["FactsLabel"]),
                Paragraph(escape_xml(value), self.styles["FactsValue"]),
            ]
            for label, value in facts
        ]

        fact_table = Table(
            table_data,
            colWidths=[self.content_width * 0.24, self.content_width * 0.76],
        )
        fact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.palette["surface"]),
            ('LINEBELOW', (0, 0), (-1, -2), 0.35, self.palette["divider"]),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(fact_table)
        self.story.append(Spacer(1, 0.13 * inch))

    def _add_consultant_summary(self):
        """Add consultant overview details."""
        consultant = self.profile_data.get('consultant', {})
        general = self.profile_data.get('general_customizations', {})

        name = f"{consultant.get('first_name', '')} {consultant.get('last_name', '')}".strip()
        if name:
            self.story.append(Paragraph(escape_xml(name), self.styles['ConsultantName']))
        if consultant.get('title'):
            self.story.append(Paragraph(escape_xml(consultant['title']), self.styles['ConsultantTitle']))

        facts = []
        if general.get('role'):
            facts.append(("Role", str(general["role"])))
        if general.get('years_experience') is not None:
            facts.append(("Experience", f"{general['years_experience']} years"))
        if consultant.get('email'):
            facts.append(("Email", str(consultant["email"])))
        self._render_fact_panel(facts)

        focus_areas = parse_list_like(general.get("focus_areas"))
        if focus_areas:
            focus_line = "  •  ".join(escape_xml(item) for item in focus_areas)
            self.story.append(Paragraph("FOCUS AREAS", self.styles["SectionSubheader"]))
            self.story.append(Paragraph(focus_line, self.styles["DetailLine"]))
            self.story.append(Spacer(1, 0.04 * inch))

        if general.get('motto'):
            quote_table = Table(
                [[Paragraph(f'"{escape_xml(general["motto"])}"', self.styles['Quote'])]],
                colWidths=[self.content_width],
            )
            quote_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.palette["surface_alt"]),
                ('LINEBEFORE', (0, 0), (0, 0), 2.4, self.accent_color),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            self.story.append(quote_table)

    def _format_project_duration(self, project: dict) -> Optional[str]:
        """Create a readable project duration label."""
        start = format_display_date(project.get('start_date'))
        end = format_display_date(project.get('end_date'))
        if project.get('is_ongoing'):
            end = "Present"

        if start and end:
            return f"{start} - {end}"
        return start or end

    def _build_entry_block(
        self,
        *,
        title: str,
        metadata: Optional[list[str]] = None,
        description: Optional[str] = None,
        detail_lines: Optional[list[str]] = None,
    ):
        """Create a card-like block and keep it intact on one page when possible."""
        block = [Paragraph(escape_xml(title), self.styles['EntryTitle'])]

        if metadata:
            cleaned_metadata = [escape_xml(item) for item in metadata if item]
            if cleaned_metadata:
                block.append(Paragraph("  •  ".join(cleaned_metadata), self.styles['MetaLine']))

        if description:
            block.append(Paragraph(format_multiline_text(description), self.styles['BodyText']))

        if detail_lines:
            for line in detail_lines:
                if line:
                    block.append(Paragraph(line, self.styles['DetailLine']))

        card = Table([[block]], colWidths=[self.content_width])
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.palette["surface"]),
            ('BOX', (0, 0), (-1, -1), 0.65, self.palette["divider"]),
            ('TOPPADDING', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return KeepTogether([card, Spacer(1, 0.08 * inch)])

    def _add_projects(self):
        """Add professional experience section."""
        projects = self.profile_data.get('blocks_by_type', {}).get('project', [])
        if not projects:
            return

        self._add_section_header('Professional Experience')

        for project in projects:
            metadata = []
            if project.get('client_name'):
                metadata.append(f"Client: {project['client_name']}")
            if project.get('role'):
                metadata.append(f"Role: {project['role']}")

            duration = self._format_project_duration(project)
            if duration:
                metadata.append(f"Timeline: {duration}")

            details = []
            technologies = parse_list_like(project.get('technologies'))
            if technologies:
                details.append(
                    f"<b>Technologies:</b> {escape_xml(', '.join(technologies))}"
                )

            self.story.append(
                self._build_entry_block(
                    title=project.get('title', 'Untitled Project'),
                    metadata=metadata,
                    description=project.get('description'),
                    detail_lines=details,
                )
            )

    def _add_skills(self):
        """Add skills section as a proficiency-sorted list inside a compact grid."""
        skills = self.profile_data.get('blocks_by_type', {}).get('skill', [])
        if not skills:
            return

        self._add_section_header('Skills Overview')

        level_order = ['Expert', 'Advanced', 'Proficient', 'Basic']
        level_colors = {
            'Expert': '#009E73',
            'Advanced': '#0072B2',
            'Proficient': '#E69F00',
            'Basic': '#7A7A7A',
        }

        def normalize_level(raw_level: Optional[str]) -> str:
            text = str(raw_level or '').strip().lower()
            if not text:
                return 'Proficient'
            if any(token in text for token in ('expert', 'master', 'principal', 'lead')):
                return 'Expert'
            if any(token in text for token in ('advanced', 'senior')):
                return 'Advanced'
            if any(token in text for token in ('basic', 'beginner', 'novice', 'junior')):
                return 'Basic'
            return 'Proficient'

        level_rank = {level: index for index, level in enumerate(level_order)}
        skill_entries = []
        for skill in skills:
            title = str(skill.get('title') or 'Skill').strip() or 'Skill'
            normalized_level = normalize_level(skill.get('level'))
            skill_entries.append((title, normalized_level))

        skill_entries.sort(key=lambda entry: (level_rank[entry[1]], entry[0].lower()))
        level_totals = {level: 0 for level in level_order}
        for _, level in skill_entries:
            level_totals[level] += 1

        summary_cells = [
            Paragraph(
                "<b>%d</b><br/><font size='7.2' color='#64748B'>SKILLS</font>" % len(skills),
                self.styles['SkillSummaryMetric'],
            ),
        ]
        for level in level_order:
            summary_cells.append(
                Paragraph(
                    "<b>%d</b><br/><font size='7.2' color='%s'>%s</font>"
                    % (level_totals[level], level_colors[level], level.upper()),
                    self.styles['SkillSummaryMetric'],
                )
            )

        summary_table = Table(
            [summary_cells],
            colWidths=[self.content_width / len(summary_cells)] * len(summary_cells),
        )
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.palette["surface"]),
            ('BOX', (0, 0), (-1, -1), 0.65, self.palette["divider"]),
            ('LINEAFTER', (0, 0), (-2, 0), 0.30, self.palette["divider"]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        self.story.append(summary_table)
        self.story.append(Spacer(1, 0.08 * inch))

        legend_cells = []
        for level in level_order:
            legend_cells.append(
                Paragraph(
                    "<font color='%s'>&#9679;</font> <font size='7.2' color='#64748B'>%s</font>"
                    % (level_colors[level], level.upper()),
                    self.styles['SkillMatrixHeader'],
                )
            )

        legend_table = Table(
            [legend_cells],
            colWidths=[self.content_width / len(legend_cells)] * len(legend_cells),
        )
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.45, self.palette["divider"]),
            ('LINEAFTER', (0, 0), (-2, 0), 0.30, self.palette["divider"]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        self.story.append(legend_table)
        self.story.append(Spacer(1, 0.06 * inch))

        grid_columns = 3
        grid_data = []
        for index in range(0, len(skill_entries), grid_columns):
            row_entries = skill_entries[index:index + grid_columns]
            row = []
            for title, level in row_entries:
                row.append(Paragraph(
                    "<font size='9.2' color='%s'>&#9679;</font> %s"
                    % (level_colors[level], escape_xml(title)),
                    self.styles['SkillGridItem'],
                ))
            while len(row) < grid_columns:
                row.append(Paragraph("&nbsp;", self.styles['SkillGridItem']))
            grid_data.append(row)

        skills_grid = Table(
            grid_data,
            colWidths=[self.content_width / grid_columns] * grid_columns,
        )
        skills_grid.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.30, self.palette["divider"]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        self.story.append(skills_grid)
        self.story.append(Spacer(1, 0.06 * inch))

    def _add_misc(self):
        """Add miscellaneous section for talks, blogs, websites, and similar items."""
        misc_blocks = self.profile_data.get('blocks_by_type', {}).get('misc', [])
        if not misc_blocks:
            return

        self._add_section_header('Additional Highlights')

        for item in misc_blocks:
            self.story.append(
                self._build_entry_block(
                    title=item.get('title', 'Additional Item'),
                    description=item.get('content'),
                )
            )

    def _add_certifications(self):
        """Add certifications section."""
        certs = self.profile_data.get('blocks_by_type', {}).get('certification', [])
        if not certs:
            return

        self._add_section_header('Certifications')

        for cert in certs:
            metadata = []
            if cert.get('issuing_organization'):
                metadata.append(f"Issuer: {cert['issuing_organization']}")
            if cert.get('issue_date'):
                issue_date = format_display_date(cert.get('issue_date'))
                if issue_date:
                    metadata.append(f"Issued: {issue_date}")
            if cert.get('expiry_date'):
                expiry_date = format_display_date(cert.get('expiry_date'))
                if expiry_date:
                    metadata.append(f"Expires: {expiry_date}")

            details = []
            if cert.get('credential_id'):
                details.append(f"<b>Credential ID:</b> {escape_xml(str(cert['credential_id']))}")
            if cert.get('credential_url'):
                details.append(f"<b>Credential URL:</b> {escape_xml(str(cert['credential_url']))}")

            self.story.append(
                self._build_entry_block(
                    title=cert.get('title', 'Certification'),
                    metadata=metadata,
                    detail_lines=details,
                )
            )

    def generate(self) -> bytes:
        """Generate the PDF and return as bytes."""
        self._add_header()
        self._add_consultant_summary()
        self._add_projects()
        self._add_skills()
        self._add_certifications()
        self._add_misc()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin + 0.16 * inch,
            title=f"Profile - {self.profile_data.get('consultant', {}).get('first_name', 'Consultant')}",
            author=self.company_name or "Profile Export",
        )

        doc.build(
            self.story,
            onFirstPage=self._draw_page_chrome,
            onLaterPages=self._draw_page_chrome,
        )

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes


def export_profile_to_pdf(
    profile_data: dict,
    company_name: Optional[str] = None,
    accent_color: Optional[str] = DEFAULT_ACCENT_COLOR,
    template: str = "default",
) -> tuple[bytes, str]:
    """
    Export profile to PDF

    Returns:
        tuple of (pdf_bytes, suggested_filename)
    """
    if template != "default":
        raise ValueError(f"Unsupported export template: {template}")

    if isinstance(profile_data, str):
        profile_data = json.loads(profile_data)

    generator = ProfilePDFGenerator(
        profile_data=profile_data,
        company_name=company_name,
        accent_color=accent_color,
    )

    pdf_bytes = generator.generate()

    # Generate filename
    consultant = profile_data.get('consultant', {})
    consultant_name = f"{consultant.get('first_name', '')} {consultant.get('last_name', '')}".strip()

    if consultant_name:
        filename = sanitize_filename(f"{consultant_name}_Profile.pdf")
    else:
        filename = "consultant_profile.pdf"

    return pdf_bytes, filename
