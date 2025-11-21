// frontend/src/theme.ts
/**
 * LAB 색상값을 RGB로 변환
 * LAB: L=0.084, A=-0.016, B=-0.171
 *
 * 이 색상은 매우 어두운 청록색 계열입니다.
 * UI 가독성을 위해 이 색상을 기본으로 하되, 밝기를 조정한 변형들을 생성합니다.
 */

// LAB to XYZ to RGB 변환
function labToRgb(l: number, a: number, b: number): string {
  // LAB 값이 0-1 범위인 경우 0-100 범위로 변환
  const L = l * 100;
  const A = a * 100;
  const B = b * 100;

  // LAB to XYZ
  let y = (L + 16) / 116;
  let x = A / 500 + y;
  let z = y - B / 200;

  const x3 = Math.pow(x, 3);
  const y3 = Math.pow(y, 3);
  const z3 = Math.pow(z, 3);

  x = x3 > 0.008856 ? x3 : (x - 16 / 116) / 7.787;
  y = y3 > 0.008856 ? y3 : (y - 16 / 116) / 7.787;
  z = z3 > 0.008856 ? z3 : (z - 16 / 116) / 7.787;

  // D65 illuminant
  x *= 95.047;
  y *= 100.000;
  z *= 108.883;

  // XYZ to RGB
  let r = x * 0.032406 + y * -0.015372 + z * -0.004986;
  let g = x * -0.009689 + y * 0.018758 + z * 0.000415;
  let b_rgb = x * 0.000557 + y * -0.002040 + z * 0.010570;

  // Apply gamma correction
  r = r > 0.0031308 ? 1.055 * Math.pow(r, 1 / 2.4) - 0.055 : 12.92 * r;
  g = g > 0.0031308 ? 1.055 * Math.pow(g, 1 / 2.4) - 0.055 : 12.92 * g;
  b_rgb = b_rgb > 0.0031308 ? 1.055 * Math.pow(b_rgb, 1 / 2.4) - 0.055 : 12.92 * b_rgb;

  // Clamp to 0-255
  const R = Math.max(0, Math.min(255, Math.round(r * 255)));
  const G = Math.max(0, Math.min(255, Math.round(g * 255)));
  const B_rgb = Math.max(0, Math.min(255, Math.round(b_rgb * 255)));

  return `rgb(${R}, ${G}, ${B_rgb})`;
}

// RGB to Hex 변환
function rgbToHex(rgb: string): string {
  const match = rgb.match(/\d+/g);
  if (!match) return '#000000';
  const r = parseInt(match[0]);
  const g = parseInt(match[1]);
  const b = parseInt(match[2]);
  return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
}

// 밝기 조정 함수
function adjustLightness(rgb: string, factor: number): string {
  const match = rgb.match(/\d+/g);
  if (!match) return rgb;

  let [r, g, b] = match.map(x => parseInt(x));

  // HSL로 변환하여 밝기 조정
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  // 밝기 조정
  l = Math.max(0, Math.min(1, l * factor));

  // HSL to RGB
  const hue2rgb = (p: number, q: number, t: number) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 1/2) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  };

  let r_new, g_new, b_new;
  if (s === 0) {
    r_new = g_new = b_new = l;
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r_new = hue2rgb(p, q, h + 1/3);
    g_new = hue2rgb(p, q, h);
    b_new = hue2rgb(p, q, h - 1/3);
  }

  const R = Math.round(r_new * 255);
  const G = Math.round(g_new * 255);
  const B = Math.round(b_new * 255);

  return `rgb(${R}, ${G}, ${B})`;
}

// 기본 색상 (LAB: 0.084, -0.016, -0.171)
const baseColorRgb = labToRgb(0.084, -0.016, -0.171);
const baseColor = rgbToHex(baseColorRgb);

// 색상이 너무 어두워서 실용적인 UI를 위해 밝기를 조정한 변형 생성
export const theme = {
  // 원본 색상 (매우 어두운 청록색)
  primary: baseColor,
  primaryRgb: baseColorRgb,

  // 밝기 조정 변형들 (UI 가독성을 위해)
  primaryLight: rgbToHex(adjustLightness(baseColorRgb, 15)),    // 훨씬 밝게
  primaryMedium: rgbToHex(adjustLightness(baseColorRgb, 8)),    // 중간 밝기
  primaryDark: baseColor,                                        // 원본 (어두움)

  // 실제 사용할 주요 색상 (청록색 계열 유지하되 밝기 조정)
  accent: '#1a7b7f',      // 청록색 (주요 버튼, 강조)
  accentHover: '#156669',  // 청록색 호버
  accentLight: '#d4f1f2',  // 연한 청록색 (배경)

  // 보조 색상
  success: '#4CAF50',
  warning: '#FF9800',
  error: '#f44336',
  info: '#2196F3',

  // 중성 색상
  text: {
    primary: '#333333',
    secondary: '#666666',
    light: '#999999',
    white: '#ffffff',
  },

  background: {
    primary: '#ffffff',
    secondary: '#f8f9fa',
    tertiary: '#f0f2f5',
    dark: baseColor,  // 원본 어두운 색상
  },

  border: {
    light: '#e0e0e0',
    medium: '#ddd',
    dark: '#ccc',
  },
};

// 그라데이션
export const gradients = {
  primary: `linear-gradient(135deg, ${theme.accent} 0%, ${theme.accentHover} 100%)`,
  light: `linear-gradient(135deg, ${theme.accentLight} 0%, #ffffff 100%)`,
};

// 그림자
export const shadows = {
  small: '0 2px 4px rgba(0, 0, 0, 0.1)',
  medium: '0 4px 8px rgba(0, 0, 0, 0.1)',
  large: '0 8px 16px rgba(0, 0, 0, 0.15)',
  colored: `0 4px 12px rgba(26, 123, 127, 0.3)`,
};

export default theme;
