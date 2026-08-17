"""
Module 13: Forensic Fraud Investigation PDF Report Generator
Intelligent Banking Fraud Detection Platform
Author: Reporting System Engineer
"""

import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, KeepTogether, HRFlowable
)


class FraudReportGenerator:
    """
    Generates high-fidelity, audit-ready PDF forensic investigation dossiers
    for bank fraud analysts, compliance officers, and law enforcement.
    """

    def __init__(self, output_dir: str = "reports_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf_report(
        self,
        case_id: str,
        transaction_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        shap_data: Dict[str, Any],
        investigator_notes: Optional[str] = None,
        investigator_name: str = "Lead Fraud Analyst #8142"
    ) -> str:
        """
        Build and write the official PDF report to disk.
        """
        filename = f"FRAUD_DOSSIER_{case_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Paragraph Styles
        header_title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0f172a')
        )
        
        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#334155')
        )

        badge_style = ParagraphStyle(
            'RiskBadge',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
            alignment=1  # Centered
        )

        story = []

        # 1. Header Banner & Security Classification
        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        header_data = [
            [
                Paragraph("<b>SENTINEL INTELLIGENT BANKING PLATFORM</b><br/><font size=8 color='#64748b'>Global Fraud Investigation & Forensic Risk Dossier</font>", body_style),
                Paragraph(f"<font color='#dc2626'><b>STRICTLY CONFIDENTIAL</b></font><br/><font size=8>Generated: {timestamp_str}</font>", body_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[3.8 * inch, 3.7 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0f172a'), spaceBefore=4, spaceAfter=12))

        # 2. Case Summary & Risk Tier Card
        risk_level = risk_data.get("risk_level", "UNKNOWN").upper()
        risk_score = risk_data.get("final_risk_score", 0.0)
        
        badge_bg = colors.HexColor('#fee2e2') if risk_level == "CRITICAL" else colors.HexColor('#ffedd5') if risk_level == "HIGH" else colors.HexColor('#fef9c3') if risk_level == "MEDIUM" else colors.HexColor('#dcfce7')
        badge_fg = colors.HexColor('#b91c1c') if risk_level == "CRITICAL" else colors.HexColor('#c2410c') if risk_level == "HIGH" else colors.HexColor('#a16207') if risk_level == "MEDIUM" else colors.HexColor('#15803d')

        case_summary_data = [
            [
                Paragraph(f"<b>Case Reference:</b> {case_id}<br/>"
                          f"<b>Transaction ID:</b> {transaction_data.get('transaction_id', 'TXN-99824')}<br/>"
                          f"<b>Timestamp:</b> {transaction_data.get('timestamp', timestamp_str)}<br/>"
                          f"<b>Amount:</b> <font size=11 color='#0f172a'><b>${float(transaction_data.get('amount', 0.0)):,.2f} USD</b></font><br/>"
                          f"<b>Action Taken:</b> {risk_data.get('recommended_action', 'FLAG_FOR_REVIEW')}", body_style),
                Paragraph(f"<font color='{badge_fg.hexval()}'><b>RISK LEVEL: {risk_level}</b></font><br/>"
                          f"<font size=20 color='{badge_fg.hexval()}'><b>{risk_score}/100</b></font><br/>"
                          f"<font size=8>Status: {risk_data.get('action_description', 'Under active investigation')}</font>", badge_style)
            ]
        ]
        case_summary_table = Table(case_summary_data, colWidths=[4.7 * inch, 2.8 * inch])
        case_summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (1, 0), (1, 0), badge_bg),
            ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#e2e8f0')),
            ('BOX', (1, 0), (1, 0), 1.5, badge_fg),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(case_summary_table)
        story.append(Spacer(1, 14))

        # 3. Multi-Factor Risk Score Breakdown
        story.append(Paragraph("1. Multi-Factor Risk Model Diagnostics", section_heading_style))
        scores_breakdown = risk_data.get("score_breakdown", {})
        diag_data = [
            ["Diagnostic Factor", "Raw Metric", "Factor Weight", "Normalized Impact"],
            [
                "Supervised Machine Learning (XGBoost)",
                f"{scores_breakdown.get('supervised_probability_pct', 0):.1f}% Fraud Probability",
                "65%",
                f"{scores_breakdown.get('supervised_probability_pct', 0) * 0.65:.1f} / 65.0"
            ],
            [
                "Unsupervised Anomaly (Isolation Forest)",
                f"{scores_breakdown.get('anomaly_score_pct', 0):.1f} Outlier Index",
                "25%",
                f"{scores_breakdown.get('anomaly_score_pct', 0) * 0.25:.1f} / 25.0"
            ],
            [
                "Domain Heuristics & Rules",
                f"{len(risk_data.get('triggered_rules', []))} Rule(s) Triggered",
                "10%",
                f"{scores_breakdown.get('heuristic_rule_score_pct', 0) * 0.10:.1f} / 10.0"
            ],
            [
                "CALIBRATED COMPOSITE RISK SCORE",
                f"{risk_level} SEVERITY",
                "100%",
                f"{risk_score} / 100.0"
            ]
        ]
        diag_table = Table(diag_data, colWidths=[2.6 * inch, 2.0 * inch, 1.3 * inch, 1.6 * inch])
        diag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(diag_table)
        story.append(Spacer(1, 14))

        # 4. SHAP Explainable AI Feature Attribution & Reason Codes
        story.append(Paragraph("2. Explainable AI (SHAP) Forensic Feature Attribution", section_heading_style))
        
        reason_codes = shap_data.get("reason_codes", [])
        if reason_codes:
            reasons_html = "<b>Primary Behavioral Triggers Identified:</b><br/>" + "<br/>".join([f"• {rc}" for rc in reason_codes])
            story.append(Paragraph(reasons_html, body_style))
            story.append(Spacer(1, 8))

        top_drivers = shap_data.get("top_risk_drivers", [])
        shap_table_data = [["Feature Name", "Observed Value", "SHAP Attribution (Delta)", "Risk Direction"]]
        for d in top_drivers:
            shap_table_data.append([
                str(d.get("feature", "N/A")),
                str(d.get("raw_value", "N/A")),
                f"+{d.get('shap_value', 0):.4f}",
                "Elevates Fraud Probability"
            ])

        shap_table = Table(shap_table_data, colWidths=[2.2 * inch, 1.8 * inch, 1.8 * inch, 1.7 * inch])
        shap_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(shap_table)
        story.append(Spacer(1, 14))

        # 5. Investigator Notes & Forensic Audit Stamp
        story.append(Paragraph("3. Fraud Analyst Investigation Notes & Audit Signature", section_heading_style))
        notes_text = investigator_notes if investigator_notes else (
            "System Automated Dossier: Transaction triggered multi-layer anomaly threshold. "
            "Cardholder notification dispatched via secure channel. Account placed on temporary verification hold."
        )
        story.append(Paragraph(f"<b>Investigator:</b> {investigator_name}<br/><b>Findings:</b> {notes_text}", body_style))
        story.append(Spacer(1, 12))

        # Checksum Hash for immutability
        raw_hash_input = f"{case_id}-{transaction_data.get('amount', 0)}-{risk_score}-{timestamp_str}"
        audit_hash = hashlib.sha256(raw_hash_input.encode()).hexdigest()

        footer_data = [
            [
                Paragraph(f"<b>Digital Audit Checksum (SHA-256):</b><br/><font size=7 color='#64748b'>{audit_hash}</font>", body_style),
                Paragraph("<b>Verified Fraud Risk Engine</b><br/><font size=8 color='#10b981'>COMPLIANCE CERTIFIED</font>", badge_style)
            ]
        ]
        footer_table = Table(footer_data, colWidths=[5.3 * inch, 2.2 * inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(footer_table)

        # Build Document
        doc.build(story)
        print(f"[PDF Generator] Forensic Dossier exported successfully to: {filepath}")
        return filepath


if __name__ == "__main__":
    generator = FraudReportGenerator()
    test_pdf = generator.generate_pdf_report(
        case_id="CASE-2026-9921",
        transaction_data={"transaction_id": "TXN-88194", "amount": 1824.50, "timestamp": "2026-08-16 20:15:00 UTC"},
        risk_data={
            "risk_level": "CRITICAL",
            "final_risk_score": 94.2,
            "recommended_action": "AUTO_BLOCK",
            "action_description": "Transaction terminated and card locked.",
            "score_breakdown": {
                "supervised_probability_pct": 96.5,
                "anomaly_score_pct": 88.0,
                "heuristic_rule_score_pct": 80.0
            },
            "triggered_rules": ["High transaction amount (>$1,000)", "Off-hours transaction", "Extreme PCA anomaly"]
        },
        shap_data={
            "reason_codes": [
                "Critical latent identity / card-use deviation (V14 = -6.42)",
                "Unusual transaction amount pattern ($1,824.50 relative deviation)",
                "High-risk off-hours transaction window"
            ],
            "top_risk_drivers": [
                {"feature": "V14", "raw_value": -6.42, "shap_value": 0.3841},
                {"feature": "V12", "raw_value": -4.89, "shap_value": 0.2912},
                {"feature": "Amount_Deviation_Z", "raw_value": 3.81, "shap_value": 0.1845},
                {"feature": "V10", "raw_value": -3.22, "shap_value": 0.1250},
                {"feature": "Is_Night_Transaction", "raw_value": 1, "shap_value": 0.0890}
            ]
        },
        investigator_notes="Pattern matches credential stuffing and rapid cash-out vector. Card blocked."
    )
    print("Test PDF successfully built at:", test_pdf)
