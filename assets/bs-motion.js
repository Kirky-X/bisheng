/*!
 * bs-motion · bisheng 自研动效内核
 * 覆盖 deck 所需 API: to / fromTo / set / timeline / stagger / kill / progress
 * 新增特效: spring 弹簧缓动、splitText 文本揭示、drawSVG 描边生长、smoothSwitch 平滑切换
 * 零依赖。仅操作 transform / opacity / stroke-dashoffset,不动布局。
 */
(function (global) {
  "use strict";

  /* ---------- 缓动 ---------- */
  function easeOut(t) {
    return 1 - Math.pow(1 - t, 3);
  } // power3.out 等价
  function easeOut2(t) {
    return 1 - Math.pow(1 - t, 2);
  } // power2.out 等价
  function spring(stiffness, damping) {
    stiffness = stiffness || 120;
    damping = damping || 14;
    return function (t) {
      // 阻尼谐振子近似,归一化到 0..1,允许轻微过冲
      var w = Math.sqrt(stiffness),
        z = damping / (2 * w);
      if (z >= 1) return easeOut(t);
      var wd = w * Math.sqrt(1 - z * z);
      return (
        1 -
        Math.exp(-z * w * t) *
          (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t))
      );
    };
  }
  var globalDefaults = {};
  var EASES = {
    "power3.out": easeOut,
    "power2.out": easeOut2,
    none: function (t) {
      return t;
    },
  };

  /* ---------- 属性应用 ---------- */
  function apply(el, v) {
    if (!el || !el.style) return;
    for (var k in v) {
      if (!Object.prototype.hasOwnProperty.call(v, k)) continue;
      var val = v[k];
      if (k === "autoAlpha") {
        el.style.opacity = val;
        el.style.visibility = +val > 0 ? "visible" : "hidden";
      } else if (k === "y") {
        el.style.transform =
          (el.style.transform || "").replace(/translateY\([^)]*\)/, "") +
          " translateY(" +
          val +
          "px)";
      } else if (k === "x") {
        el.style.transform =
          (el.style.transform || "").replace(/translateX\([^)]*\)/, "") +
          " translateX(" +
          val +
          "px)";
      } else if (k === "scaleY") {
        el.style.transform =
          (el.style.transform || "").replace(/scaleY\([^)]*\)/, "") +
          " scaleY(" +
          val +
          ")";
      } else if (k === "scaleX") {
        el.style.transform =
          (el.style.transform || "").replace(/scaleX\([^)]*\)/, "") +
          " scaleX(" +
          val +
          ")";
      } else if (k === "transformOrigin") {
        el.style.transformOrigin = val;
      } else if (k === "clearProps") {
        if (val === "transform" || val === true || val === "all")
          el.style.transform = "";
      } else el.style[k] = val;
    }
  }
  function targetsOf(t) {
    if (!t) return [];
    if (typeof t === "string")
      return Array.prototype.slice.call(document.querySelectorAll(t));
    if (t.nodeType) return [t];
    return Array.prototype.slice.call(t);
  }

  /* ---------- Tween ---------- */
  function Tween(targets, vars, fromVars) {
    var self = this;
    var tg = targetsOf(targets);
    this._targets = tg;
    this.duration = (vars.duration || 0.5) * 1000;
    this._ease =
      typeof vars.ease === "function" ? vars.ease : EASES[vars.ease] || easeOut;
    this._delay = (vars.delay || 0) * 1000;
    this._stagger = (vars.stagger || 0) * 1000;
    this._t0 = 0;
    this._paused = !!vars.paused;
    this._done = false;
    this._killed = false;
    this._onUpdate = vars.onUpdate;
    this._onComplete = vars.onComplete;
    this._props = {};
    for (var k in vars) {
      if (
        [
          "duration",
          "ease",
          "delay",
          "stagger",
          "paused",
          "onUpdate",
          "onComplete",
          "overwrite",
        ].indexOf(k) >= 0
      )
        continue;
      this._props[k] = vars[k];
    }
    this._from = fromVars || null;
    this._startValues = [];
    this._stateVars = null;
    // 纯对象补间(state.v 用于数字滚动)
    if (tg.length === 0 && targets && typeof targets === "object") {
      this._stateVars = { obj: targets, keys: this._props };
      this._startValues.push(this._copyState(targets, this._props));
    }
    // 构造即初始化:fromTo 立刻应用初态(immediateRender)
    if (fromVars && Object.keys(fromVars).length && tg.length) this._init();
  }
  Tween.prototype._copyState = function (obj, props) {
    var s = {};
    for (var k in props) s[k] = +obj[k] || 0;
    return s;
  };
  Tween.prototype._init = function () {
    if (this._initialized) return;
    this._initialized = true;
    var self = this;
    this._targets.forEach(function (el, i) {
      var from = self._from || {};
      var start = {};
      var keys = Object.keys(from).length ? from : self._props;
      for (var k in keys) {
        if (k === "clearProps") continue;
        if (k === "autoAlpha")
          start[k] = parseFloat(getComputedStyle(el).opacity) || 0;
        else if (k === "y" || k === "x") start[k] = 0;
        else if (k === "scaleY" || k === "scaleX") start[k] = 1;
      }
      self._startValues[i] = start;
      if (from && Object.keys(from).length) apply(el, from); // immediateRender
    });
    if (this._from && Object.keys(this._from).length) {
      var frm = this._from;
      this._targets.forEach(function (el) { apply(el, frm); });
    }
  };
  Tween.prototype.seek = function (ms) {
    this._init();
    var p =
      this.duration > 0
        ? Math.min(1, Math.max(0, (ms - this._delay) / this.duration))
        : 1;
    var e = this._ease(p);
    var self = this;
    this._targets.forEach(function (el, i) {
      var staggerMs = self._stagger || 0;
      var perTargetP = self.duration > 0
        ? Math.min(1, Math.max(0, (ms - self._delay - i * staggerMs) / self.duration)) : 1;
      var pe = self._ease(perTargetP);
      var out = {},
        start = self._startValues[i] || {},
        from = self._from || {};
      for (var k in self._props) {
        if (k === "clearProps") continue;
        var a =
          (Object.prototype.hasOwnProperty.call(from, k)
            ? +from[k]
            : +start[k]) || 0;
        var b = +self._props[k] || 0;
        out[k] = a + (b - a) * pe;
      }
      if (p >= 1 && self._props.clearProps)
        out.clearProps = self._props.clearProps;
      apply(el, out);
    });
    if (this._stateVars) {
      var sv = this._stateVars,
        s0 = this._startValues[0] || {};
      for (var k2 in sv.keys)
        sv.obj[k2] = (+s0[k2] || 0) + (+sv.keys[k2] - (+s0[k2] || 0)) * e;
    }
    if (this._onUpdate) this._onUpdate.call(this);
    // 有 stagger 时,全部目标完成需要额外 (n-1)*stagger
    var maxMs = this._delay + Math.max(0, this._targets.length - 1) * (this._stagger || 0) + this.duration;
    if (ms >= maxMs && !this._done) {
      this._done = true;
      if (this._onComplete) this._onComplete();
    }
    return this;
  };
  Tween.prototype.progress = function (v) {
    var total = this.duration + Math.max(0, this._targets.length - 1) * (this._stagger || 0);
    return this.seek(v * total + this._delay);
  };
  Tween.prototype.kill = function () {
    this._killed = true;
    return this;
  };
  Tween.prototype.isActive = function () {
    return !this._done && !this._killed;
  };
  Tween.prototype.play = function () {
    this._paused = false;
    return this;
  };
  Tween.prototype.pause = function () {
    this._paused = true;
    return this;
  };

  /* ---------- Timeline ---------- */
  function Timeline(vars) {
    vars = vars || {};
    this._items = [];
    this._defaults = vars.defaults || {};
    this._pos = 0;
    this._t0 = 0;
    this._done = false;
    this._killed = false;
  }
  function mergeVars(defaults, vars) {
    var out = {};
    for (var g in globalDefaults) out[g] = globalDefaults[g];
    for (var k in defaults) out[k] = defaults[k];
    for (var k2 in vars) out[k2] = vars[k2];
    return out;
  }
  Timeline.prototype.fromTo = function (targets, from, to, pos) {
    this._done = false;
    var v = mergeVars(this._defaults, to);
    var tw = new Tween(targets, v, from);
    var at =
      pos === undefined ? this._pos : typeof pos === "number" ? pos : this._pos;
    this._items.push({ tw: tw, at: at });
    if (pos === undefined)
      this._pos =
        at + (tw.duration + tw._stagger * (tw._targets.length - 1)) / 1000;
    return this;
  };
  Timeline.prototype.to = function (targets, vars, pos) {
    this._done = false;
    var tw = new Tween(targets, mergeVars(this._defaults, vars));
    var at = typeof pos === "number" ? pos : this._pos;
    this._items.push({ tw: tw, at: at });
    if (pos === undefined) this._pos = at + tw.duration / 1000;
    return this;
  };
  Timeline.prototype.set = function (targets, vars, pos) {
    var tw = new Tween(targets, mergeVars(this._defaults, vars));
    tw.duration = 0;
    this._items.push({ tw: tw, at: typeof pos === "number" ? pos : this._pos });
    return this;
  };
  Timeline.prototype.add = function (child, pos) {
    this._done = false;
    if (child instanceof Tween)
      this._items.push({
        tw: child,
        at: typeof pos === "number" ? pos : this._pos,
      });
    return this;
  };
  Timeline.prototype.addLabel = function () {
    return this;
  };
  Timeline.prototype.seek = function (ms) {
    var allDone = true; // 空 timeline 视为已完成,proxy 可从调度器移除
    this._items.forEach(function (it) {
      var local = ms - it.at * 1000;
      if (local >= -it.tw._delay) it.tw.seek(Math.max(0, local));
      if (!it.tw._done) allDone = false;
    });
    if (allDone) this._done = true;
    return this;
  };
  Timeline.prototype.progress = function (v) {
    var total = 0;
    this._items.forEach(function (it) {
      total = Math.max(
        total,
        it.at * 1000 +
          it.tw.duration +
          it.tw._delay +
          it.tw._stagger * Math.max(0, it.tw._targets.length - 1),
      );
    });
    return this.seek(v * total);
  };
  Timeline.prototype.kill = function () {
    this._killed = true;
    this._items.forEach(function (it) {
      it.tw.kill();
    });
    return this;
  };
  Timeline.prototype.isActive = function () {
    return this._items.length > 0 && !this._done && !this._killed;
  };
  Timeline.prototype.pause = function () {
    this._items.forEach(function (it) {
      it.tw.pause();
    });
    return this;
  };
  Timeline.prototype.play = function () {
    this._items.forEach(function (it) {
      it.tw.play();
    });
    return this;
  };

  /* ---------- 调度器 ---------- */
  var active = [];
  function tick(now) {
    for (var i = active.length - 1; i >= 0; i--) {
      var tw = active[i];
      if (tw._killed || tw._done) {
        active.splice(i, 1);
        continue;
      }
      if (tw._paused) continue;
      if (tw._proxy) {
        if (!tw._t0) tw._t0 = now;
        tw.seek(now - tw._t0);
        if (!tw.isActive()) active.splice(i, 1);
        continue;
      }
      if (!tw._t0) tw._t0 = now;
      var local = now - tw._t0;
      // stagger:每个目标按索引延迟
      if (tw._stagger && tw._targets.length > 1) {
        var maxLocal = now - tw._t0;
        tw._targets.forEach(function (_, idx) {
          /* stagger 由 seek 内部处理,这里推进主进度 */
        });
        local = maxLocal;
      }
      tw.seek(local);
      if (tw._done) active.splice(i, 1);
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  /* ---------- 公共 API ---------- */
  var BSM = {
    version: "1.0.0",
    to: function (targets, vars) {
      var tw = new Tween(targets, vars);
      active.push(tw);
      return tw;
    },
    fromTo: function (targets, from, to) {
      var tw = new Tween(targets, to, from);
      active.push(tw);
      return tw;
    },
    set: function (targets, vars) {
      var tw = new Tween(targets, vars);
      tw.duration = 0;
      tw.seek(0);
      return tw;
    },
    timeline: function (vars) {
      var tl = new Timeline(vars);
      var proxy = {
        _killed: false,
        _done: false,
        _paused: false,
        _t0: 0,
        _proxy: true,
        _targets: [],
        _delay: 0,
        _stagger: 0,
        seek: function (ms) {
          tl.seek(ms);
        },
        isActive: function () {
          return tl.isActive();
        },
        kill: function () {
          this._killed = true;
          tl.kill();
        },
        pause: function () {
          tl.pause();
        },
        play: function () {
          tl.play();
        },
      };
      active.push(proxy);
      return tl;
    },
    kill: function (tw) {
      if (tw) tw.kill();
    },
    defaults: function (v) { globalDefaults = v || {}; },
    globalTimeline: {
      getChildren: function () {
        return [];
      },
    },
    spring: spring,
    ease: EASES,

    /* 新特效 1:弹簧入场(返回 tween vars) */
    springVars: function (stiffness, damping) {
      return { ease: spring(stiffness, damping), duration: 0.9 };
    },

    /* 新特效 2:文本逐字/逐行揭示 */
    splitText: function (el, mode) {
      if (!el || !el.textContent) return [];
      mode = mode || "chars";
      var text = el.textContent,
        frag = document.createDocumentFragment(),
        out = [];
      var units = mode === "lines" ? text.split(/(<br>|\n)/i) : text.split("");
      units.forEach(function (u) {
        if (u === "<br>" || u === "\n") {
          frag.appendChild(document.createElement("br"));
          return;
        }
        var s = document.createElement("span");
        s.className =
          "bs-split " + (mode === "lines" ? "bs-split-line" : "bs-split-char");
        s.style.display = "inline-block";
        s.style.whiteSpace = "pre";
        s.textContent = u;
        frag.appendChild(s);
        out.push(s);
      });
      el.textContent = "";
      el.appendChild(frag);
      return out;
    },

    /* 新特效 3:SVG 描边生长 */
    drawSVG: function (pathEl, duration) {
      if (!pathEl || !pathEl.getTotalLength) return null;
      var len = pathEl.getTotalLength();
      pathEl.style.strokeDasharray = len;
      pathEl.style.strokeDashoffset = len;
      return BSM.to(pathEl, {
        strokeDashoffset: 0,
        duration: duration || 1.2,
        ease: "power2.out",
      });
    },

    /* 新特效 4:平滑切换(翻页时的 crossfade + 轻缩放) */
    smoothSwitch: function (fromSec, toSec) {
      if (!fromSec || !toSec || fromSec === toSec) return;
      if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      toSec.classList.add("bs-switch-in");
      fromSec.classList.add("bs-switch-out");
      setTimeout(function () {
        toSec.classList.remove("bs-switch-in");
        fromSec.classList.remove("bs-switch-out");
      }, 620);
    },
  };

  global.BSMotion = BSM;
})(window);
