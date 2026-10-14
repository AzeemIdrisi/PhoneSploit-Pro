import { cn } from "@/lib/utils";

type SectionIntroProps = {
  index: string;
  label: string;
  title: React.ReactNode;
  subtitle?: string;
  align?: "left" | "center";
  className?: string;
};

export function SectionIntro({
  index,
  label,
  title,
  subtitle,
  align = "left",
  className,
}: SectionIntroProps) {
  return (
    <div
      className={cn(
        "mb-12 sm:mb-16 max-w-3xl",
        align === "center" && "mx-auto text-center",
        className,
      )}
    >
      <p className="section-eyebrow mb-3">
        [ {index} / {label} ]
      </p>
      <h2 className="section-title glitch-hover">{title}</h2>
      {subtitle && (
        <p
          className={cn(
            "section-subtitle",
            align === "center" && "mx-auto",
          )}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
}
