import { QuestionSuggestion } from '../services/api';

const STOP_WORDS = new Set([
  'a', 'about', 'an', 'and', 'are', 'as', 'at', 'be', 'can', 'do', 'does',
  'for', 'from', 'how', 'i', 'in', 'is', 'it', 'me', 'my', 'of', 'on', 'or',
  'please', 'the', 'this', 'to', 'what', 'when', 'where', 'which', 'who',
  'why', 'with', 'you',
]);

/**
 * Normalizes a question to a canonical key identifying its underlying question type/template.
 * Questions that belong to the same procedural family (e.g. Procedure Part 1, Procedure Part 7)
 * produce the same key so suggestions show only one representative question per type.
 */
export function getQuestionTypeKey(suggestion: QuestionSuggestion): string {
  const q = suggestion.question.trim().toLowerCase();
  const qNorm = q
    .replace(/[-\s]*(?:operational\s+workflow\s+for|procedure|part|step|phase)\s*#?\d+.*?(in the e-gp system\??|$)/gi, ' in the e-gp system')
    .replace(/-\s*procedure\s+part\s+\d+.*?(in the e-gp system\??|$)/gi, ' in the e-gp system')
    .replace(/procedure\s+part\s+\d+/gi, '')
    .replace(/part\s+\d+/gi, '')
    .replace(/step\s+\d+/gi, '')
    .replace(/\d+/g, '')
    .replace(/[^\p{L}\p{N}\s]+/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return `${suggestion.module.trim().toLowerCase()}:::${qNorm}`;
}

/**
 * Filters a list of question suggestions so that only ONE question per type/template is retained.
 * Keeps the first occurrence (or top-ranked occurrence).
 */
export function deduplicateQuestionSuggestions(
  questions: QuestionSuggestion[],
): QuestionSuggestion[] {
  const seen = new Set<string>();
  const result: QuestionSuggestion[] = [];

  for (const suggestion of questions) {
    const key = getQuestionTypeKey(suggestion);
    if (!seen.has(key)) {
      seen.add(key);
      result.push(suggestion);
    }
  }

  return result;
}

export function searchQuestionSuggestions(
  query: string,
  questions: QuestionSuggestion[],
): QuestionSuggestion[] {
  const terms = query
    .trim()
    .toLocaleLowerCase()
    .split(/[^\p{L}\p{N}]+/u)
    .filter((term) => term.length > 1 && !STOP_WORDS.has(term));

  if (terms.length === 0) return [];

  const matched = questions
    .map((suggestion) => {
      const question = suggestion.question.toLocaleLowerCase();
      const searchableText = `${question} ${suggestion.module.toLocaleLowerCase()}`;
      const tokens = searchableText.split(/[^\p{L}\p{N}]+/u);
      const matchedTerms = terms.filter((term) =>
        tokens.some((token) => token === term || token.startsWith(term)),
      );
      const exactMatches = terms.filter((term) => tokens.includes(term)).length;
      return {
        suggestion,
        matchedCount: matchedTerms.length,
        exactMatches,
        phraseMatch: question.includes(query.trim().toLocaleLowerCase()),
      };
    })
    .filter(({ matchedCount }) => matchedCount === terms.length)
    .sort((a, b) =>
      Number(b.phraseMatch) - Number(a.phraseMatch) ||
      b.exactMatches - a.exactMatches ||
      a.suggestion.question_number - b.suggestion.question_number,
    )
    .map(({ suggestion }) => suggestion);

  return deduplicateQuestionSuggestions(matched);
}
