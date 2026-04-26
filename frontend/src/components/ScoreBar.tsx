type ScoreBarProps = {
  label: string;
  value: number;
  variant: "match" | "interest" | "combined";
  size?: "sm" | "md";
};

const variantClass: Record<ScoreBarProps["variant"], string> = {
  match: "bg-gradient-primary",
  interest: "bg-gradient-score",
  combined: "bg-gradient-score"
};

export function ScoreBar({
  label,
  value,
  variant,
  size = "md"
}: ScoreBarProps) {
  return (
    <div className="w-full">
      <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span className="tabular-nums font-semibold text-foreground">
          {Math.round(value)}%
        </span>
      </div>
      <div
        className={size === "sm" ? "h-2 rounded-full bg-muted" : "h-2.5 rounded-full bg-muted"}
      >
        <div
          className={`${variantClass[variant]} h-full rounded-full`}
          style={{ width: `${Math.max(0, Math.min(value, 100))}%` }}
        />
      </div>
    </div>
  );
}
