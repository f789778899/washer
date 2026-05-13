import { X } from "lucide-react";
import { Language, copy } from "../lib/i18n";

type TutorialModalProps = {
  language: Language;
  onClose: () => void;
};

export function TutorialModal({ language, onClose }: TutorialModalProps) {
  const t = copy[language];
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-panel tutorial-modal">
        <div className="modal-header">
          <h2>{t.tutorial.title}</h2>
          <button className="icon-button" onClick={onClose} title={t.menu.close}>
            <X size={18} />
          </button>
        </div>
        <ol className="tutorial-list">
          {t.tutorial.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </div>
    </div>
  );
}

