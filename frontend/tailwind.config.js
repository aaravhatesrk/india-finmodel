/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: "#0f766e",
          dark: "#0b5a54",
        },
        coral: {
          DEFAULT: "#ff6b6b",
          dark: "#e85555",
        },
        sand: {
          DEFAULT: "#f7efe5",
          dark: "#efe2d1",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 4px 20px rgba(15, 118, 110, 0.08)",
      },
    },
  },
  plugins: [],
};
