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

  /**
   * exportInvestigative(config)
   *
   * config = {
   *   title          : string,
   *   journalist     : string,
   *   date           : string,
   *   status         : string,
   *   lead           : string,
   *   prefatory      : string,
   *   threads        : [{code, name, question}],
   *   entities       : [{name, type, description, statedPosition, contradictions: string[]}],
   *   sources        : [{title, tier, sourceType, date, url, excerpt}],
   *   claims         : [{statement, confidence, sourceIds, entities, legalRisks, threads}],
   *   openQuestions  : [{text}],
   *   sourceTierLabel: {1: string, 2: string, 3: string, 0: string},
   *   briefText      : string
   * }
   */
  function exportInvestigative(config) {
    if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') {
      alert('PDF library is still loading. Please wait a moment and try again.');
      return;
    }

    const jsPDF = (window.jspdf && window.jspdf.jsPDF) || window.jsPDF;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const W = doc.internal.pageSize.getWidth();
    const H = doc.internal.pageSize.getHeight();
    const MARGIN = 18;
    const COL_W = W - MARGIN * 2;
    const CONTENT_BOTTOM = 272;
    let y = MARGIN;

    const DARK   = [5, 10, 26];
    const ACCENT = [59, 139, 255];
    const GOLD   = [240, 192, 64];
    const MUTED  = [122, 139, 168];
    const WHITE  = [232, 236, 244];
    const GREEN  = [48, 209, 88];
    const AMBER  = [255, 159, 10];
    const RED    = [255, 59, 48];
    const PURPLE = [167, 139, 255];

    function setFill(arr) { doc.setFillColor(...arr); }
    function setDraw(arr) { doc.setDrawColor(...arr); }
    function setTxtColor(arr) { doc.setTextColor(...arr); }
    function safeText(value, fallback) {
      return String(value == null || value === '' ? (fallback || '') : value);
    }
    function asArray(value) {
      return Array.isArray(value) ? value : [];
    }
    function checkPageBreak(required) {
      required = required || 0;
      if (y + required > CONTENT_BOTTOM) {
        doc.addPage();
        y = MARGIN;
        return true;
      }
      return false;
    }
    function lineBlockHeight(lines, lineHeight, padding) {
      return (lines.length || 1) * lineHeight + (padding || 0);
    }
    function sectionHeader(title, color, minHeight) {
      checkPageBreak(minHeight || 14);
      setFill(color || ACCENT);
      doc.rect(MARGIN - 4, y, 4, 6, 'F');
      setTxtColor(color || ACCENT);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.text(String(title).toUpperCase(), MARGIN + 2, y + 4.2);
      setDraw([30, 50, 90]);
      doc.line(MARGIN - 4, y + 6, W - MARGIN + 4, y + 6);
      y += 10;
    }
    function fillTextBlock(text, x, width, options) {
      options = options || {};
      const lines = doc.splitTextToSize(safeText(text), width);
      if (options.color) setTxtColor(options.color);
      doc.setFont('helvetica', options.fontStyle || 'normal');
      doc.setFontSize(options.fontSize || 8);
      doc.text(lines, x, y);
      y += lines.length * (options.lineHeight || 4.8) + (options.after || 0);
      return lines;
    }
    function pill(text, x, topY, color, textColor, paddingX) {
      const label = safeText(text).toUpperCase();
      const px = paddingX || 2.3;
      doc.setFont('courier', 'bold');
      doc.setFontSize(7);
      const width = doc.getTextWidth(label) + px * 2;
      setFill(color);
      doc.roundedRect(x, topY, width, 5.2, 1.6, 1.6, 'F');
      setTxtColor(textColor || DARK);
      doc.text(label, x + px, topY + 3.55);
      return width;
    }
    function measurePillWidth(text, paddingX) {
      const px = paddingX || 2.3;
      doc.setFont('courier', 'bold');
      doc.setFontSize(7);
      return doc.getTextWidth(safeText(text).toUpperCase()) + px * 2;
    }
    function tierColor(tier) {
      if (Number(tier) === 1) return GREEN;
      if (Number(tier) === 2) return ACCENT;
      if (Number(tier) === 3) return PURPLE;
      return MUTED;
    }
    function confidenceColor(confidence) {
      if (confidence === 'CONFIRMED') return GREEN;
      if (confidence === 'CORROBORATED') return ACCENT;
      if (confidence === 'ALLEGED') return AMBER;
      return RED;
    }
    function entityTypeColor(type) {
      const value = safeText(type).toUpperCase();
      if (value === 'PERSON') return PURPLE;
      if (value === 'ORG' || value === 'ORGANIZATION') return ACCENT;
      if (value === 'COMPANY') return ACCENT;
      if (value === 'DOCUMENT') return GOLD;
      return MUTED;
    }
    function resolveSourceTitle(sourceId, sources) {
      if (sourceId == null) return null;
      if (typeof sourceId === 'number' && sources[sourceId]) return safeText(sources[sourceId].title, 'Untitled source');
      if (/^\d+$/.test(String(sourceId)) && sources[Number(sourceId)]) return safeText(sources[Number(sourceId)].title, 'Untitled source');
      for (let i = 0; i < sources.length; i++) {
        const source = sources[i];
        if (source && (source.id === sourceId || source.code === sourceId || source.slug === sourceId || source.title === sourceId)) {
          return safeText(source.title, 'Untitled source');
        }
      }
      return safeText(sourceId);
    }

    const threads = asArray(config.threads);
    const entities = asArray(config.entities);
    const sourceLookup = asArray(config.sources).slice();
    const sources = sourceLookup.slice();
    const claims = asArray(config.claims);
    const openQuestions = asArray(config.openQuestions);
    const sourceTierLabel = config.sourceTierLabel || {};

    const sourceOrder = { 1: 0, 2: 1, 3: 2, 0: 3 };
    sources.sort(function(a, b) {
      const aTier = sourceOrder.hasOwnProperty(a && a.tier) ? sourceOrder[a.tier] : 4;
      const bTier = sourceOrder.hasOwnProperty(b && b.tier) ? sourceOrder[b.tier] : 4;
      if (aTier !== bTier) return aTier - bTier;
      return safeText(a && a.date).localeCompare(safeText(b && b.date));
    });

    const legalRiskClaims = claims.filter(function(claim) {
      return asArray(claim && claim.legalRisks).length > 0;
    });
    const legalRiskSummary = {};
    legalRiskClaims.forEach(function(claim) {
      asArray(claim.legalRisks).forEach(function(risk) {
        const key = safeText(risk);
        legalRiskSummary[key] = (legalRiskSummary[key] || 0) + 1;
      });
    });

    setFill(DARK);
    doc.rect(0, 0, W, 30, 'F');

    setTxtColor(ACCENT);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.text('AxiomZero', MARGIN, 13);

    setTxtColor(MUTED);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.text(AZ_ORG + ' — ' + AZ_UBI, MARGIN, 19);
    doc.text(AZ_DOMAIN + '  ·  ' + AZ_EMAIL, MARGIN, 24);

    setTxtColor(WHITE);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text(safeText(config.title, 'Investigative Dossier'), W - MARGIN, 13, { align: 'right', maxWidth: 92 });

    setTxtColor(MUTED);
    doc.setFont('courier', 'normal');
    doc.setFontSize(7.5);
    doc.text(
      [
        'Journalist: ' + safeText(config.journalist, 'Unassigned'),
        'Date: ' + safeText(config.date, new Date().toISOString().slice(0, 10)),
        'Status: ' + safeText(config.status, 'Draft')
      ],
      W - MARGIN,
      19,
      { align: 'right' }
    );

    y = 36;

    checkPageBreak(22);
    setFill(WHITE);
    setDraw([214, 221, 232]);
    doc.roundedRect(MARGIN, y, COL_W, 17, 2, 2, 'FD');
    setTxtColor(DARK);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.text('Methodology', MARGIN + 4, y + 5);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.4);
    doc.text(
      'Source standard: Tier 1 (primary record) · Tier 2 (independent reporting) · Tier 3 (context/background)',
      MARGIN + 4,
      y + 9.2
    );
    doc.text(
      'Confidence scale: CONFIRMED · CORROBORATED · ALLEGED · UNVERIFIED',
      MARGIN + 4,
      y + 13.2
    );
    doc.setFont('courier', 'bold');
    setTxtColor(ACCENT);
    doc.text('AXIOM OSINT TRIANGULATION CHAIN', W - MARGIN - 4, y + 13.2, { align: 'right' });
    y += 23;

    if (threads.length) {
      sectionHeader('Thread Tracking', ACCENT, 20);
      const codeW = 28;
      const nameW = 46;
      const questionW = COL_W - codeW - nameW;
      const tableX = MARGIN;
      function drawThreadHeader() {
        const headerY = y;
        setFill([16, 24, 43]);
        doc.rect(tableX, headerY, COL_W, 7, 'F');
        setTxtColor(WHITE);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7.5);
        doc.text('Code', tableX + 2, headerY + 4.6);
        doc.text('Thread Name', tableX + codeW + 2, headerY + 4.6);
        doc.text('Core Question', tableX + codeW + nameW + 2, headerY + 4.6);
        y += 7;
      }

      drawThreadHeader();

      threads.forEach(function(thread, index) {
        const questionLines = doc.splitTextToSize(safeText(thread.question), questionW - 4);
        const nameLines = doc.splitTextToSize(safeText(thread.name), nameW - 4);
        const rowHeight = Math.max(lineBlockHeight(questionLines, 4.6, 4), lineBlockHeight(nameLines, 4.6, 4), 9);
        if (checkPageBreak(rowHeight + 9)) drawThreadHeader();

        setDraw([221, 226, 235]);
        doc.rect(tableX, y, COL_W, rowHeight, 'S');
        const threadColor = [ACCENT, PURPLE, GOLD, GREEN][index % 4];
        pill(safeText(thread.code, 'T' + (index + 1)), tableX + 2, y + 2, threadColor, DARK, 2);

        setTxtColor(DARK);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7.8);
        doc.text(nameLines, tableX + codeW + 2, y + 4.5);
        doc.setFont('helvetica', 'normal');
        doc.text(questionLines, tableX + codeW + nameW + 2, y + 4.5);
        y += rowHeight;
      });
      y += 4;
    }

    if (config.prefatory) {
      sectionHeader('Prefatory Note', GOLD, 18);
      setTxtColor(MUTED);
      doc.setFont('helvetica', 'italic');
      doc.setFontSize(8.5);
      const prefatoryLines = doc.splitTextToSize(safeText(config.prefatory), COL_W);
      checkPageBreak(prefatoryLines.length * 4.8 + 4);
      doc.text(prefatoryLines, MARGIN, y);
      y += prefatoryLines.length * 4.8 + 5;
    }

    if (config.lead) {
      sectionHeader('Investigative Lead', ACCENT, 18);
      setTxtColor(DARK);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8.6);
      const leadLines = doc.splitTextToSize(safeText(config.lead), COL_W);
      checkPageBreak(leadLines.length * 4.8 + 4);
      doc.text(leadLines, MARGIN, y);
      y += leadLines.length * 4.8 + 5;
    }

    if (entities.length) {
      sectionHeader('Entities', PURPLE, 20);
      entities.forEach(function(entity) {
        const descLines = doc.splitTextToSize(safeText(entity.description), COL_W - 12);
        const positionLines = doc.splitTextToSize('Stated position: ' + safeText(entity.statedPosition, 'Not stated'), COL_W - 12);
        const contradictions = asArray(entity.contradictions);
        const contradictionLines = contradictions.length
          ? doc.splitTextToSize('Contradictions: ' + contradictions.join(' · '), COL_W - 12)
          : [];
        const cardHeight = 10 + descLines.length * 4.4 + positionLines.length * 4.4 + (contradictionLines.length ? contradictionLines.length * 4.4 + 3 : 0);

        checkPageBreak(cardHeight + 4);
        setFill([247, 249, 252]);
        setDraw([220, 226, 235]);
        doc.roundedRect(MARGIN, y, COL_W, cardHeight, 2, 2, 'FD');

        pill(safeText(entity.type, 'ENTITY'), MARGIN + 3, y + 3, entityTypeColor(entity.type), DARK, 2.2);
        setTxtColor(DARK);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(9);
        doc.text(safeText(entity.name, 'Unnamed entity'), MARGIN + 27, y + 6.9);

        let innerY = y + 12;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.text(descLines, MARGIN + 3, innerY);
        innerY += descLines.length * 4.4;

        setTxtColor(MUTED);
        doc.text(positionLines, MARGIN + 3, innerY);
        innerY += positionLines.length * 4.4;

        if (contradictionLines.length) {
          setTxtColor(AMBER);
          doc.setFont('helvetica', 'bold');
          doc.text(contradictionLines, MARGIN + 3, innerY + 1);
        }

        y += cardHeight + 4;
      });
    }

    if (sources.length) {
      sectionHeader('Sources', GREEN, 20);
      sources.forEach(function(source) {
        const titleLines = doc.splitTextToSize(safeText(source.title, 'Untitled source'), COL_W - 12);
        const meta = [safeText(source.sourceType, 'Unknown type'), safeText(source.date, 'Undated')].filter(Boolean).join('  ·  ');
        const urlLines = source.url ? doc.splitTextToSize(safeText(source.url), COL_W - 12) : [];
        const excerptLines = source.excerpt ? doc.splitTextToSize('“' + safeText(source.excerpt) + '”', COL_W - 12) : [];
        const tierLabel = safeText(sourceTierLabel[source.tier], 'Tier ' + safeText(source.tier, '0'));
        const cardHeight = 11 + titleLines.length * 4.2 + (meta ? 4.4 : 0) + urlLines.length * 4 + (excerptLines.length ? excerptLines.length * 4.2 + 3 : 0);

        checkPageBreak(cardHeight + 4);
        setDraw([222, 228, 236]);
        doc.roundedRect(MARGIN, y, COL_W, cardHeight, 2, 2, 'S');
        pill(tierLabel, MARGIN + 3, y + 3, tierColor(source.tier), DARK, 2.4);

        setTxtColor(DARK);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8.8);
        doc.text(titleLines, MARGIN + 3, y + 11);

        let innerY = y + 11 + titleLines.length * 4.2;
        if (meta) {
          setTxtColor(MUTED);
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(7.6);
          doc.text(meta, MARGIN + 3, innerY);
          innerY += 4.4;
        }
        if (urlLines.length) {
          setTxtColor(ACCENT);
          doc.text(urlLines, MARGIN + 3, innerY);
          innerY += urlLines.length * 4;
        }
        if (excerptLines.length) {
          setTxtColor(MUTED);
          doc.setFont('helvetica', 'italic');
          doc.text(excerptLines, MARGIN + 3, innerY + 1);
        }

        y += cardHeight + 4;
      });
    }

    if (claims.length) {
      sectionHeader('Claims & Confidence', ACCENT, 20);
      claims.forEach(function(claim) {
        const sourceNames = asArray(claim.sourceIds).map(function(sourceId) {
          return resolveSourceTitle(sourceId, sourceLookup);
        }).filter(Boolean);
        const entityNames = asArray(claim.entities).map(function(name) { return safeText(name); }).filter(Boolean);
        const threadRefs = asArray(claim.threads).map(function(code) { return safeText(code); }).filter(Boolean);
        const legalRisks = asArray(claim.legalRisks).map(function(risk) { return safeText(risk); }).filter(Boolean);

        const statementLines = doc.splitTextToSize(safeText(claim.statement), COL_W - 10);
        const sourceLines = sourceNames.length ? doc.splitTextToSize('Sources: ' + sourceNames.join(' · '), COL_W - 10) : [];
        const entityLines = entityNames.length ? doc.splitTextToSize('Entities: ' + entityNames.join(' · '), COL_W - 10) : [];
        const threadLines = threadRefs.length ? doc.splitTextToSize('Threads: ' + threadRefs.join(' · '), COL_W - 10) : [];
        let legalRiskRows = 0;
        if (legalRisks.length) {
          let rowWidth = 0;
          legalRiskRows = 1;
          legalRisks.forEach(function(risk) {
            const width = measurePillWidth(risk, 2.3) + 2;
            if (rowWidth && rowWidth + width > COL_W - 6) {
              legalRiskRows += 1;
              rowWidth = 0;
            }
            rowWidth += width;
          });
        }
        const cardHeight = 12 + statementLines.length * 4.4 + sourceLines.length * 4.2 + entityLines.length * 4.2 + threadLines.length * 4.2 + (legalRisks.length ? legalRiskRows * 6 + 2 : 0);

        checkPageBreak(cardHeight + 4);
        setFill([248, 250, 253]);
        setDraw([220, 226, 235]);
        doc.roundedRect(MARGIN, y, COL_W, cardHeight, 2, 2, 'FD');
        pill(safeText(claim.confidence, 'UNVERIFIED'), MARGIN + 3, y + 3, confidenceColor(claim.confidence), DARK, 2.4);

        let innerY = y + 11;
        setTxtColor(DARK);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8.4);
        doc.text(statementLines, MARGIN + 3, innerY);
        innerY += statementLines.length * 4.4;

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7.6);
        if (sourceLines.length) {
          setTxtColor(MUTED);
          doc.text(sourceLines, MARGIN + 3, innerY);
          innerY += sourceLines.length * 4.2;
        }
        if (entityLines.length) {
          doc.text(entityLines, MARGIN + 3, innerY);
          innerY += entityLines.length * 4.2;
        }
        if (threadLines.length) {
          doc.text(threadLines, MARGIN + 3, innerY);
          innerY += threadLines.length * 4.2;
        }
        if (legalRisks.length) {
          let pillX = MARGIN + 3;
          innerY += 1;
          legalRisks.forEach(function(risk) {
            const riskWidth = measurePillWidth(risk, 2.3);
            if (pillX + riskWidth > W - MARGIN - 3) {
              pillX = MARGIN + 3;
              innerY += 6;
            }
            pill(risk, pillX, innerY, RED, WHITE, 2.3);
            pillX += riskWidth + 2;
          });
        }

        y += cardHeight + 4;
      });
    }

    if (openQuestions.length) {
      sectionHeader('Open Questions', GOLD, 16);
      setTxtColor(DARK);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8.3);
      openQuestions.forEach(function(item) {
        const questionLines = doc.splitTextToSize('• ' + safeText(item.text), COL_W);
        checkPageBreak(questionLines.length * 4.8 + 1);
        doc.text(questionLines, MARGIN, y);
        y += questionLines.length * 4.8 + 1.5;
      });
      y += 2;
    }

    if (Object.keys(legalRiskSummary).length) {
      sectionHeader('Legal Risk Summary', RED, 18);
      Object.keys(legalRiskSummary).forEach(function(risk) {
        const summaryLines = doc.splitTextToSize(risk + ' — flagged in ' + legalRiskSummary[risk] + ' claim(s).', COL_W - 16);
        checkPageBreak(summaryLines.length * 4.6 + 4);
        pill(risk, MARGIN, y, RED, WHITE, 2.4);
        setTxtColor(DARK);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.text(summaryLines, MARGIN + 30, y + 3.6);
        y += Math.max(summaryLines.length * 4.6, 6) + 2;
      });
      y += 2;
    }

    if (config.briefText) {
      sectionHeader('Appendix — Plain-Text Brief', MUTED, 18);
      setTxtColor(MUTED);
      doc.setFont('courier', 'normal');
      doc.setFontSize(7.2);
      const briefLines = doc.splitTextToSize(safeText(config.briefText), COL_W);
      briefLines.forEach(function(line) {
        checkPageBreak(4.3);
        doc.text(line, MARGIN, y);
        y += 4.3;
      });
      y += 2;
    }

    checkPageBreak(18);
    setFill(DARK);
    doc.roundedRect(MARGIN, y, COL_W, 13, 2, 2, 'F');
    setTxtColor(WHITE);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.text('⚠ AXIOM OUTPUT — FOR HUMAN REVIEW ONLY. NOT READY TO PUBLISH.', MARGIN + 4, y + 8);
    y += 17;

    const pageCount = doc.internal.getNumberOfPages();
    for (let p = 1; p <= pageCount; p++) {
      doc.setPage(p);
      setFill(DARK);
      doc.rect(0, H - 14, W, 14, 'F');
      setTxtColor(MUTED);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(6.5);
      doc.text(AZ_ORG + ' — ' + AZ_UBI + '  ·  ' + AZ_DISCLAIMER, MARGIN, H - 7);
      doc.text('Page ' + p + ' / ' + pageCount, W - MARGIN, H - 7, { align: 'right' });
    }

    const filename = 'AZ-Investigative-Dossier-' + safeText(config.title, 'export').replace(/[^\w.-]+/g, '-').replace(/^-+|-+$/g, '') + '.pdf';
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
  global.AZDossier = { export: exportDossier, exportInvestigative: exportInvestigative, attach: attachDossierButton };

})(window);
