import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "var(--color-ink)",
        sand: "var(--color-sand)",
        frost: "var(--color-frost)",
        ocean: "var(--color-ocean)",
        ember: "var(--color-ember)"
      },
      boxShadow: {
        panel: "0 16px 60px rgba(8, 35, 44, 0.18)"
      },
      borderRadius: {
        panel: "28px"
      }
    }
  },
  plugins: []
};

export default config;
