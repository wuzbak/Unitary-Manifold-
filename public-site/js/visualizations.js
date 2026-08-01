/**
 * visualizations.js — Three.js 5D Kaluza-Klein Visualizations
 *
 * Provides:
 * - KK5DAnimation: Animated 5D compact extra dimension visualization
 * - KKTowerViz: Kaluza-Klein mass tower visualization
 * - BraidViz: (5,7) braid topology visualization
 */

"use strict";

// ── KK 5D Animation (Landing Page Hero) ──────────────────────────────────────
class KK5DAnimation {
  /**
   * @param {HTMLElement} container
   * @param {object} opts
   */
  constructor(container, opts = {}) {
    this.container = container;
    this.opts = {
      nw: opts.nw ?? 5,
      kcs: opts.kcs ?? 74,
      interactive: opts.interactive ?? true,
      ...opts,
    };

    this.scene    = null;
    this.camera   = null;
    this.renderer = null;
    this.objects  = {};
    this.frame    = 0;
    this.animId   = null;
    this.mouse    = { x: 0, y: 0 };

    this._init();
  }

  _init() {
    if (typeof THREE === "undefined") {
      this._fallback();
      return;
    }

    const w = this.container.clientWidth  || 800;
    const h = this.container.clientHeight || 500;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x050a1a);
    this.scene.fog = new THREE.Fog(0x050a1a, 20, 80);

    // Camera
    this.camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 200);
    this.camera.position.set(0, 4, 18);
    this.camera.lookAt(0, 0, 0);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0x112244, 2);
    this.scene.add(ambient);
    const point1 = new THREE.PointLight(0x3b8bff, 4, 50);
    point1.position.set(10, 10, 10);
    this.scene.add(point1);
    const point2 = new THREE.PointLight(0x7c4dff, 3, 50);
    point2.position.set(-10, -5, -10);
    this.scene.add(point2);

    this._buildScene();
    this._bindEvents();
    this._animate();
  }

  _buildScene() {
    const nw  = this.opts.nw;
    const kcs = this.opts.kcs;

    // ── Grid plane (4D spacetime representation) ──────────────────────────
    const gridHelper = new THREE.GridHelper(40, 20, 0x1a2a4a, 0x0d1830);
    gridHelper.position.y = -3;
    this.scene.add(gridHelper);

    // ── Central torus = compact S¹ fiber (5th dimension) ─────────────────
    const torusGeo = new THREE.TorusGeometry(3.5, 0.35, 16, 64);
    const torusMat = new THREE.MeshPhongMaterial({
      color: 0x3b8bff,
      emissive: 0x112244,
      shininess: 60,
      transparent: true,
      opacity: 0.85,
    });
    const torus = new THREE.Mesh(torusGeo, torusMat);
    torus.rotation.x = Math.PI / 2;
    this.scene.add(torus);
    this.objects.torus = torus;

    // ── Winding strands: n_w = 5 helices around the torus ─────────────────
    const strandGroup = new THREE.Group();
    for (let i = 0; i < nw; i++) {
      const hue = (i / nw) * 360;
      const color = new THREE.Color(`hsl(${200 + hue * 0.4}, 80%, 65%)`);
      const strandMat = new THREE.MeshPhongMaterial({ color, emissive: color, emissiveIntensity: 0.3 });

      const points = [];
      for (let t = 0; t <= 200; t++) {
        const theta = (t / 200) * Math.PI * 2;
        const phi   = (t / 200) * Math.PI * 2 * nw + (i / nw) * Math.PI * 2;
        const R = 3.5, r = 0.35;
        points.push(new THREE.Vector3(
          (R + r * Math.cos(phi)) * Math.cos(theta),
          r * Math.sin(phi) * 0.6,
          (R + r * Math.cos(phi)) * Math.sin(theta),
        ));
      }
      const curve = new THREE.CatmullRomCurve3(points);
      const strandGeo = new THREE.TubeGeometry(curve, 200, 0.045, 8, false);
      const strand = new THREE.Mesh(strandGeo, strandMat);
      strandGroup.add(strand);
    }
    this.scene.add(strandGroup);
    this.objects.strands = strandGroup;

    // ── KK tower: concentric rings = KK mass modes ─────────────────────────
    const towerGroup = new THREE.Group();
    for (let n = 1; n <= 4; n++) {
      const radius = 3.5 + n * 1.8;
      const opacity = 0.3 / n;
      const ringGeo = new THREE.TorusGeometry(radius, 0.03, 8, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x3b8bff,
        transparent: true,
        opacity,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.userData = { kkMode: n };
      towerGroup.add(ring);
    }
    this.scene.add(towerGroup);
    this.objects.kkTower = towerGroup;

    // ── Floating particles (gravitons) ────────────────────────────────────
    const particleCount = 120;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi   = Math.acos(2 * Math.random() - 1);
      const r     = 6 + Math.random() * 8;
      positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = (Math.random() - 0.5) * 6;
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
    }
    const partGeo = new THREE.BufferGeometry();
    partGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const partMat = new THREE.PointsMaterial({ color: 0x3b8bff, size: 0.05, transparent: true, opacity: 0.6 });
    const particles = new THREE.Points(partGeo, partMat);
    this.scene.add(particles);
    this.objects.particles = particles;

    // ── k_CS = 74 label sphere ────────────────────────────────────────────
    const sphGeo = new THREE.SphereGeometry(0.3, 16, 16);
    const sphMat = new THREE.MeshPhongMaterial({ color: 0xf0c040, emissive: 0x604810, shininess: 80 });
    const sphere = new THREE.Mesh(sphGeo, sphMat);
    sphere.position.set(0, 2, 0);
    this.scene.add(sphere);
    this.objects.sphere = sphere;
  }

  _animate() {
    this.animId = requestAnimationFrame(() => this._animate());
    this.frame++;

    const t = this.frame * 0.005;
    const nw = this.opts.nw;

    if (this.objects.torus) {
      this.objects.torus.rotation.z = t * 0.3;
    }
    if (this.objects.strands) {
      this.objects.strands.rotation.y = t * 0.25;
      this.objects.strands.rotation.x = Math.sin(t * 0.2) * 0.15;
    }
    if (this.objects.kkTower) {
      this.objects.kkTower.rotation.y = -t * 0.1;
    }
    if (this.objects.particles) {
      this.objects.particles.rotation.y = t * 0.08;
    }
    if (this.objects.sphere) {
      this.objects.sphere.position.y = 2 + Math.sin(t * 1.5) * 0.3;
    }

    // Mouse parallax
    if (this.opts.interactive) {
      this.camera.position.x += (this.mouse.x * 3 - this.camera.position.x) * 0.02;
      this.camera.position.y += (this.mouse.y * 2 + 4 - this.camera.position.y) * 0.02;
      this.camera.lookAt(0, 0, 0);
    }

    this.renderer.render(this.scene, this.camera);
  }

  _bindEvents() {
    window.addEventListener("resize", () => this._onResize());
    if (this.opts.interactive) {
      document.addEventListener("mousemove", (e) => {
        this.mouse.x = (e.clientX / window.innerWidth  - 0.5) * 2;
        this.mouse.y = (e.clientY / window.innerHeight - 0.5) * 2;
      });
    }
  }

  _onResize() {
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  _fallback() {
    this.container.innerHTML = `
      <div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;
        background:radial-gradient(ellipse at center,#0a1228 0%,#050a1a 100%);">
        <div style="text-align:center;opacity:0.5;font-family:monospace;color:#3b8bff;">
          <div style="font-size:3rem;margin-bottom:1rem">⬡</div>
          <div>5D Kaluza-Klein Geometry<br>n_w = 5 &nbsp;·&nbsp; k_CS = 74</div>
        </div>
      </div>`;
  }

  destroy() {
    if (this.animId) cancelAnimationFrame(this.animId);
    if (this.renderer) {
      this.renderer.dispose();
      this.renderer.domElement.remove();
    }
  }
}

// ── Braid Topology Visualizer (2D Canvas fallback) ────────────────────────────
class BraidViz {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {number} nw - winding number
   * @param {number} kcs - Chern-Simons level
   */
  constructor(canvas, nw = 5, kcs = 74) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.nw  = nw;
    this.kcs = kcs;
    this.frame = 0;
    this.animId = null;
    this._animate();
  }

  _draw() {
    const { canvas, ctx, nw, frame } = this;
    const W = canvas.width, H = canvas.height;
    const cx = W / 2, cy = H / 2;
    const R  = Math.min(W, H) * 0.32;

    ctx.clearRect(0, 0, W, H);

    // Background
    const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 1.5);
    bg.addColorStop(0, "#0a1228");
    bg.addColorStop(1, "#050a1a");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    const t = frame * 0.012;

    // Draw n_w winding strands
    for (let i = 0; i < nw; i++) {
      const phase = (i / nw) * Math.PI * 2;
      const hue   = 180 + (i / nw) * 120;
      ctx.beginPath();
      ctx.strokeStyle = `hsla(${hue}, 80%, 65%, 0.8)`;
      ctx.lineWidth = 1.5;

      for (let s = 0; s <= 360; s++) {
        const theta = (s / 360) * Math.PI * 2;
        const phi   = theta * nw + phase + t;
        const rx    = (R + R * 0.12 * Math.cos(phi)) * Math.cos(theta);
        const ry    = (R + R * 0.12 * Math.cos(phi)) * Math.sin(theta);
        if (s === 0) ctx.moveTo(cx + rx, cy + ry);
        else         ctx.lineTo(cx + rx, cy + ry);
      }
      ctx.stroke();
    }

    // Central torus outline
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(59,139,255,0.2)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Labels
    ctx.fillStyle = "rgba(240,192,64,0.9)";
    ctx.font      = `bold 13px monospace`;
    ctx.textAlign = "center";
    ctx.fillText(`n_w = ${nw}   k_CS = ${this.kcs}`, cx, H - 16);

    ctx.fillStyle = "rgba(59,139,255,0.7)";
    ctx.font      = "11px monospace";
    ctx.fillText(`c_s = ${(12/37).toFixed(4)}  ·  (5,7) braid`, cx, H - 32);
  }

  _animate() {
    this._draw();
    this.frame++;
    this.animId = requestAnimationFrame(() => this._animate());
  }

  destroy() {
    if (this.animId) cancelAnimationFrame(this.animId);
  }
}

// ── Pentad Orbital Visualizer (2D Canvas) ─────────────────────────────────────
class PentadOrbitalViz {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {object} opts
   */
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.opts = { speed: 1.0, ...opts };
    this.frame = 0;
    this.animId = null;
    this.bodyStates = [
      { name: "Ψ_univ",  r: 0,    phi: 0.0,   defect: 0.0, color: "#3b8bff" },
      { name: "Ψ_brain", r: 0.85, phi: 0.0,   defect: 0.0, color: "#30d158" },
      { name: "Ψ_human", r: 0.85, phi: 0.0,   defect: 0.0, color: "#ff9f0a" },
      { name: "Ψ_AI",    r: 0.85, phi: 0.0,   defect: 0.0, color: "#7c4dff" },
      { name: "β·C",     r: 0.5,  phi: 0.0,   defect: 0.0, color: "#f0c040" },
    ];
    // Orbital parameters: each body in a pentagonal orbit
    const n5 = 5;
    for (let i = 0; i < n5; i++) {
      this.bodyStates[i].orbitPhase = (i / n5) * Math.PI * 2;
      this.bodyStates[i].orbitSpeed = 0.008 * (i === 0 ? 0 : 1) * this.opts.speed;
    }
    this._animate();
  }

  _draw() {
    const { canvas, ctx, frame, bodyStates } = this;
    const W = canvas.width, H = canvas.height;
    const cx = W / 2, cy = H / 2;
    const baseR = Math.min(W, H) * 0.35;

    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = "#050a1a";
    ctx.fillRect(0, 0, W, H);

    // Draw orbit ring
    ctx.beginPath();
    ctx.arc(cx, cy, baseR * 0.85, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(59,139,255,0.1)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Update orbit phases
    for (let i = 1; i < 5; i++) {
      bodyStates[i].orbitPhase += bodyStates[i].orbitSpeed;
    }

    // Compute positions
    const positions = bodyStates.map((b, i) => {
      if (i === 0) return { x: cx, y: cy };
      const r = i === 4 ? baseR * 0.5 : baseR * 0.85;
      return {
        x: cx + r * Math.cos(b.orbitPhase),
        y: cy + r * Math.sin(b.orbitPhase),
      };
    });

    // Draw coupling lines (pentagonal connections)
    for (let i = 0; i < 5; i++) {
      for (let j = i + 1; j < 5; j++) {
        const p1 = positions[i], p2 = positions[j];
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        const alpha = bodyStates[4].phi > 0.1 ? 0.12 : 0.03;  // trust-dependent
        ctx.strokeStyle = `rgba(59,139,255,${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }
    }

    // Draw bodies
    bodyStates.forEach((body, i) => {
      const pos = positions[i];
      const r = i === 0 ? 18 : i === 4 ? 10 : 13;

      // Glow
      const glow = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, r * 2.5);
      const [h, s, l] = [body.color];
      glow.addColorStop(0, body.color + "55");
      glow.addColorStop(1, body.color + "00");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, r * 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Body
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);
      ctx.fillStyle = body.color;
      ctx.fill();

      // Label
      ctx.fillStyle = "rgba(255,255,255,0.8)";
      ctx.font = "10px monospace";
      ctx.textAlign = "center";
      ctx.fillText(body.name, pos.x, pos.y + r + 14);
    });

    // Stability indicator
    const stability = bodyStates.every((b, i) => i === 0 || b.defect < 0.1);
    ctx.fillStyle = stability ? "#30d158" : "#ff453a";
    ctx.font = "bold 11px monospace";
    ctx.textAlign = "left";
    ctx.fillText(stability ? "▲ STABLE ORBIT" : "▼ COLLAPSE", 10, H - 10);
  }

  _animate() {
    this._draw();
    this.frame++;
    this.animId = requestAnimationFrame(() => this._animate());
  }

  setTrustLevel(phi) {
    this.bodyStates[4].phi = Math.max(0, Math.min(1, phi));
  }

  destroy() {
    if (this.animId) cancelAnimationFrame(this.animId);
  }
}

// ── Chart.js wrapper for physics plots ────────────────────────────────────────
const PhysicsCharts = {
  /**
   * Plot w₀-wₐ dark energy plane
   * @param {HTMLCanvasElement} canvas
   */
  drawDEPlane(canvas) {
    if (typeof Chart === "undefined") return;
    const ctx = canvas.getContext("2d");

    // UM prediction point
    const umPoint   = { x: -1.0, y: 0.0 };
    // DESI DR2 best fit
    const desiPoint = { x: -0.727, y: -0.75 };

    new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "UM prediction (w₀=-1, wₐ=0)",
            data: [umPoint],
            pointBackgroundColor: "#30d158",
            pointRadius: 10,
            pointHoverRadius: 12,
          },
          {
            label: "DESI DR2 best fit",
            data: [desiPoint],
            pointBackgroundColor: "#ff9f0a",
            pointRadius: 8,
            pointHoverRadius: 10,
          },
          {
            // ΛCDM
            label: "ΛCDM (w₀=-1, wₐ=0)",
            data: [{ x: -1.0, y: 0.0 }],
            pointBackgroundColor: "#3b8bff",
            pointStyle: "crossRot",
            pointRadius: 12,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#7a8ba8", font: { size: 11 } } },
          tooltip: { backgroundColor: "#0d1830", titleColor: "#e8ecf4", bodyColor: "#7a8ba8" },
        },
        scales: {
          x: {
            title: { display: true, text: "w₀", color: "#7a8ba8" },
            ticks:  { color: "#7a8ba8" },
            grid:   { color: "#1a2a4a" },
            min: -2, max: 0,
          },
          y: {
            title: { display: true, text: "wₐ", color: "#7a8ba8" },
            ticks:  { color: "#7a8ba8" },
            grid:   { color: "#1a2a4a" },
            min: -2, max: 0.5,
          },
        },
      },
    });
  },

  /**
   * Draw Lean4 theorem progress chart
   */
  drawLean4Progress(canvas, data) {
    if (typeof Chart === "undefined") return;
    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.map(d => d.name),
        datasets: [{
          label: "Theorems proved",
          data: data.map(d => d.theorems),
          backgroundColor: ["#3b8bff", "#7c4dff", "#30d158", "#f0c040"],
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: "#0d1830", bodyColor: "#7a8ba8" },
        },
        scales: {
          x: { ticks: { color: "#7a8ba8" }, grid: { color: "#1a2a4a" } },
          y: { ticks: { color: "#7a8ba8" }, grid: { color: "#1a2a4a" } },
        },
      },
    });
  },
};

// Exports
if (typeof window !== "undefined") {
  window.KK5DAnimation   = KK5DAnimation;
  window.BraidViz        = BraidViz;
  window.PentadOrbitalViz = PentadOrbitalViz;
  window.PhysicsCharts   = PhysicsCharts;
}
