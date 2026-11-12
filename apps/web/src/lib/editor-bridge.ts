/** The code in the problem page's editor, for whoever needs to read it.
 *
 *  The editor (`features/problems`) and the AI tutor (`features/tutor`)
 *  may not import each other (`tools/check_features.py`), so the editor
 *  registers a reader here and the tutor asks for the current code only
 *  when the student presses «Kodimni tekshir». One editor per page. */

export type EditorCode = { source: string; language: string };

type Reader = () => EditorCode | null;

let reader: Reader | null = null;

export function registerEditorCode(next: Reader): () => void {
  reader = next;
  return () => {
    if (reader === next) reader = null;
  };
}

export function currentEditorCode(): EditorCode | null {
  return reader ? reader() : null;
}
