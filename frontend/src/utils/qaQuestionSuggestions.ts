import { QuestionSuggestion } from '../services/api';

const STOP_WORDS = new Set([
  'a', 'about', 'an', 'and', 'are', 'as', 'at', 'be', 'can', 'do', 'does',
  'for', 'from', 'how', 'i', 'in', 'is', 'it', 'me', 'my', 'of', 'on', 'or',
  'please', 'the', 'this', 'to', 'what', 'when', 'where', 'which', 'who',
  'why', 'with', 'you',
]);

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

  return questions
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
}
