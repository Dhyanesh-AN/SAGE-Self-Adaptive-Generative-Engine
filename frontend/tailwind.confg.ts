// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
        // Note: Since your screenshot shows the app folder at the root, 
        // make sure your content paths match your actual structure:
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0A0A0A",
                surface: "#1A1A1A",
                neon: "#E4F01A",
                muted: "#888888",
            },
            fontFamily: {
                heading: ['var(--font-syncopate)', 'sans-serif'],
                mono: ['var(--font-space-grotesk)', 'sans-serif'],
            },
            boxShadow: {
                'neon': '0 0 20px rgba(228, 240, 26, 0.15)',
            }
        },
    },
    plugins: [],
};
export default config;