import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: {
        "2xl": "1200px"
      }
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))"
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))"
        }
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem"
      },
      boxShadow: {
        elegant: "0 4px 16px -4px hsl(222 47% 11% / 0.08)",
        card: "0 12px 40px -12px hsl(250 84% 60% / 0.25)"
      },
      backgroundImage: {
        "gradient-primary":
          "linear-gradient(135deg, hsl(250 84% 60%), hsl(265 90% 70%))",
        "gradient-hero":
          "linear-gradient(135deg, hsl(250 84% 60%) 0%, hsl(265 90% 70%) 50%, hsl(190 90% 60%) 100%)",
        "gradient-subtle":
          "linear-gradient(180deg, hsl(220 25% 99%), hsl(220 25% 96%))",
        "gradient-score":
          "linear-gradient(90deg, hsl(250 84% 60%), hsl(190 90% 50%))"
      }
    }
  },
  plugins: []
} satisfies Config;
