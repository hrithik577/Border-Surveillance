/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#080B0F",
        surface: "#0E141F",
        surfaceElevated: "#151F30",
        border: "#1E2C40",
        borderActive: "#2E4460",
        accentGreen: "#10B981",
        accentAmber: "#F59E0B",
        accentRed: "#EF4444",
        accentBlue: "#3B82F6",
        accentCyan: "#06B6D4",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "IBM Plex Sans", "Inter", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        md: "6px",
      },
    },
  },
  plugins: [],
};
