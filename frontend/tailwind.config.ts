import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#3b82d4", dark: "#2563ba" },
      },
    },
  },
  plugins: [],
};

export default config;
