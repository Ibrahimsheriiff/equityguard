/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg:      "#080c18",
        surface: "#0f1626",
        border:  "#1a2540",
        teal:    "#00d4aa",
        blue:    "#0099ff",
        amber:   "#f5a623",
        red:     "#ff4d6a",
        muted:   "#5a6a80",
        sub:     "#8892a4",
        text:    "#e2e8f0",
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
}