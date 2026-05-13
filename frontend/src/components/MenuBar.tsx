import { BookOpen, Download, FileDown, Languages, Moon, Sun } from "lucide-react";
import { Language, copy } from "../lib/i18n";

type MenuBarProps = {
  language: Language;
  theme: "light" | "dark";
  onLanguageChange: (language: Language) => void;
  onThemeToggle: () => void;
  onTutorial: () => void;
  onExportJob: () => void;
  onExportDocument: () => void;
};

export function MenuBar({
  language,
  theme,
  onLanguageChange,
  onThemeToggle,
  onTutorial,
  onExportJob,
  onExportDocument
}: MenuBarProps) {
  const t = copy[language].menu;
  return (
    <nav className="top-menu" aria-label="Application menu">
      <div className="menu-brand">
        <span className="brand-mark">D</span>
        <span>DocFlow Studio</span>
      </div>
      <div className="menu-controls">
        <div className="segmented-control" title={t.language}>
          <Languages size={16} />
          <button
            className={language === "zh" ? "active" : ""}
            onClick={() => onLanguageChange("zh")}
          >
            {t.chinese}
          </button>
          <button
            className={language === "en" ? "active" : ""}
            onClick={() => onLanguageChange("en")}
          >
            {t.english}
          </button>
        </div>
        <button className="toolbar-button" onClick={onThemeToggle} title={t.theme}>
          {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          <span>{theme === "dark" ? t.light : t.dark}</span>
        </button>
        <button className="toolbar-button" onClick={onTutorial} title={t.tutorial}>
          <BookOpen size={17} />
          <span>{t.tutorial}</span>
        </button>
        <button className="toolbar-button" onClick={onExportJob} title={t.exportJob}>
          <Download size={17} />
          <span>{t.exportJob}</span>
        </button>
        <button className="toolbar-button" onClick={onExportDocument} title={t.exportDoc}>
          <FileDown size={17} />
          <span>{t.exportDoc}</span>
        </button>
      </div>
    </nav>
  );
}

