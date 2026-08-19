/**
 * dossier.js — AxiomZero Dossier Export Utility
 * Generates a formatted PDF for any AZ app session.
 * Requires jsPDF (loaded from CDN in each page that uses this).
 *
 * AxiomZero Technologies & Consulting, SPC — UBI 606 239 876
 * open science artifact for human review, use at your own liability
 */

(function(global) {
  'use strict';

  const AZ_ORG   = 'AxiomZero Technologies & Consulting, SPC';
  const AZ_UBI   = 'UBI 606 239 876';
  const AZ_EMAIL = 'cpo@axiomzerospc.org';
  const AZ_DOMAIN= 'axiomzerospc.org';
  const AZ_DISCLAIMER = 'Open science artifact for human review, use at your own liability.';

  /**
   * exportDossier(config)
   *
   * config = {
   *   appName     : string          — e.g. "Ω Synthesis Engine"
   *   appId       : string          — e.g. "06-omega-synthesis"
   *   version     : string          — e.g. "v20.1"
   *   epistemic   : string          — e.g. "🔵 ADJACENT TRACK" or "⚛️ PHYSICS"
   *   inputs      : {label, value}[]
   *   outputs     : {label, value}[]
   *   notes       : string (optional)
   *   dependencies: string[]        — e.g. ["numpy", "scipy"]
   * }
   */
  function exportDossier(config) {
    if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') {
      alert('PDF library is still loading. Please wait a moment and try again.');
      return;
    }

    const jsPDF = (window.jspdf && window.jspdf.jsPDF) || window.jsPDF;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const W = doc.internal.pageSize.getWidth();
    const MARGIN = 18;
    const COL_W  = W - MARGIN * 2;
    let y = MARGIN;

    // ── Colour palette (RGB) ──────────────────────────────────────────────────
    const DARK   = [5, 10, 26];
    const ACCENT = [59, 139, 255];
    const GOLD   = [240, 192, 64];
    const MUTED  = [122, 139, 168];
    const WHITE  = [232, 236, 244];
    const GREEN  = [48, 209, 88];

    function rgb(arr) { return { r: arr[0], g: arr[1], b: arr[2] }; }
    function setFill(arr)   { doc.setFillColor(...arr); }
    function setDraw(arr)   { doc.setDrawColor(...arr); }
    function setTxtColor(arr){ doc.setTextColor(...arr); }

    // ── Header band ───────────────────────────────────────────────────────────
    setFill(DARK);
    doc.rect(0, 0, W, 28, 'F');

    setTxtColor(ACCENT);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.text('AxiomZero', MARGIN, 13);

    setTxtColor(MUTED);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.text(AZ_ORG + ' — ' + AZ_UBI, MARGIN, 19);
    doc.text(AZ_DOMAIN + '  ·  ' + AZ_EMAIL, MARGIN, 24);

    // App name (right-aligned)
    setTxtColor(WHITE);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text(config.appName, W - MARGIN, 13, { align: 'right' });
    setTxtColor(MUTED);
    doc.setFontSize(7.5);
    doc.setFont('helvetica', 'normal');
    doc.text(config.appId + '  ' + (config.version || ''), W - MARGIN, 19, { align: 'right' });

    y = 34;

    // ── Timestamp + epistemic strip ───────────────────────────────────────────
    const now = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
    setFill([13, 24, 48]);
    doc.rect(MARGIN - 4, y - 4, COL_W + 8, 10, 'F');

    setTxtColor(MUTED);
    doc.setFontSize(7.5);
    doc.text('Generated: ' + now, MARGIN, y + 2);

    const epLabel = stripEmoji(config.epistemic || 'UNCLASSIFIED');
    doc.text('Epistemic status: ' + epLabel, W - MARGIN, y + 2, { align: 'right' });
    y += 14;

    // ── Section helper ────────────────────────────────────────────────────────
    function sectionHeader(title, color) {
      color = color || ACCENT;
      setFill(color);
      doc.rect(MARGIN - 4, y, 4, 6, 'F');
      setTxtColor(color);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.text(title.toUpperCase(), MARGIN + 2, y + 4.2);
      setDraw([30, 50, 90]);
      doc.line(MARGIN - 4, y + 6, W - MARGIN + 4, y + 6);
      y += 10;
    }

    function keyVal(label, value, labelColor, valueColor) {
      labelColor = labelColor || MUTED;
      valueColor = valueColor || WHITE;
      const lines = doc.splitTextToSize(String(value), COL_W - 50);
      setTxtColor(labelColor);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8);
      doc.text(label, MARGIN, y);
      setTxtColor(valueColor);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8);
      doc.text(lines[0] || '', MARGIN + 50, y);
      y += 5.5;
      for (let i = 1; i < lines.length; i++) {
        doc.text(lines[i], MARGIN + 50, y);
        y += 5;
      }
      checkPageBreak();
    }

    function checkPageBreak() {
      if (y > 272) { doc.addPage(); y = MARGIN; }
    }

    // ── Inputs section ────────────────────────────────────────────────────────
    if (config.inputs && config.inputs.length) {
      sectionHeader('Inputs', ACCENT);
      config.inputs.forEach(function(item) {
        keyVal(item.label, item.value);
      });
      y += 4;
    }

    // ── Outputs section ───────────────────────────────────────────────────────
    if (config.outputs && config.outputs.length) {
      sectionHeader('Outputs', GREEN);
      config.outputs.forEach(function(item) {
        keyVal(item.label, item.value, MUTED, WHITE);
      });
      y += 4;
    }

    // ── Notes ─────────────────────────────────────────────────────────────────
    if (config.notes) {
      sectionHeader('Notes', GOLD);
      setTxtColor(WHITE);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8);
      const noteLines = doc.splitTextToSize(config.notes, COL_W);
      doc.text(noteLines, MARGIN, y);
      y += noteLines.length * 5 + 6;
      checkPageBreak();
    }

    // ── Dependencies ──────────────────────────────────────────────────────────
    if (config.dependencies && config.dependencies.length) {
      sectionHeader('Dependencies', MUTED);
      setTxtColor(MUTED);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(7.5);
      doc.text(config.dependencies.join('  ·  '), MARGIN, y);
      y += 8;
    }

    // ── Footer ────────────────────────────────────────────────────────────────
    const pageCount = doc.internal.getNumberOfPages();
    for (let p = 1; p <= pageCount; p++) {
      doc.setPage(p);
      const pageH = doc.internal.pageSize.getHeight();
      setFill(DARK);
      doc.rect(0, pageH - 14, W, 14, 'F');
      setTxtColor(MUTED);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(6.5);
      doc.text(AZ_ORG + ' — ' + AZ_UBI + '  ·  ' + AZ_DISCLAIMER, MARGIN, pageH - 7);
      doc.text('Page ' + p + ' / ' + pageCount, W - MARGIN, pageH - 7, { align: 'right' });
    }

    // ── Save ──────────────────────────────────────────────────────────────────
    const filename = 'AZ-Dossier-' + (config.appId || 'export') + '-' + now.slice(0, 10) + '.pdf';
    doc.save(filename);
  }

  // ── Button factory ─────────────────────────────────────────────────────────
  /**
   * attachDossierButton(buttonId, configFn)
   * configFn() should return the dossier config object at export time.
   */
  function attachDossierButton(buttonId, configFn) {
    var btn = document.getElementById(buttonId);
    if (!btn) return;
    btn.addEventListener('click', function() {
      try {
        exportDossier(configFn());
      } catch(e) {
        console.error('Dossier export error:', e);
        alert('Export failed: ' + e.message);
      }
    });
  }

  // ── Utility ────────────────────────────────────────────────────────────────
  function stripEmoji(str) {
    return str.replace(/[\u{1F300}-\u{1FFFF}\u{2600}-\u{27FF}\u{FE00}-\u{FEFF}]/gu, '').trim();
  }

  // ── Exports ────────────────────────────────────────────────────────────────
  global.AZDossier = { export: exportDossier, attach: attachDossierButton };

})(window);
