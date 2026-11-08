import { INITIAL_MANUAL_CHUNKS } from '../data/manualChunks';
import { ManualChunk } from '../types/egp';

export interface ManualQuestionSuggestion {
  question: string;
  page: number;
  topicText: string;
  searchText: string;
}

const GENERIC_TOPICS = new Set([
  'created',
  'details',
  'information',
  'introduction',
  'overview',
  'process',
  'procedure',
  'system',
  'updated',
]);

function cleanTopic(value: string): string {
  return value
    .replace(/^\s*\d+(?:\.\d+)*[.)]?\s*/, '')
    .replace(/^\s*[-–—:]+\s*/, '')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/[.;,:-]+$/, '');
}

function isUsefulTopic(topic: string): boolean {
  return topic.length >= 5 &&
    topic.length <= 110 &&
    !/^e-gp manual section\b/i.test(topic) &&
    !/^screen\s*[-–—:]?/i.test(topic) &&
    !/^page\s+\d+\b/i.test(topic) &&
    !/^(?:after|click|complete|enter|first|for users|if|in order to|once|please|select|then|this|to|upon|you)\b/i.test(topic) &&
    !(topic.split(/\s+/).length > 5 && /\b(?:am|are|be|been|being|can|click(?:ed|ing|s)?|do|does|enter(?:ed|ing|s)?|have|has|is|may|must|need(?:ed|s)?|select(?:ed|ing|s)?|shall|should|was|were|will|would)\b/i.test(topic)) &&
    !/^(?:\d+|[-–—.]+)$/.test(topic) &&
    !GENERIC_TOPICS.has(topic.toLowerCase());
}

function questionForTopic(topic: string): string {
  if (/^how to\b/i.test(topic)) {
    return `How do I ${topic.replace(/^how to\s*/i, '')}?`;
  }
  if (/^steps for\b/i.test(topic)) {
    return `What are the steps for ${topic.replace(/^steps for\s*/i, '')}?`;
  }
  if (/^how do i\b/i.test(topic)) {
    return `${topic}?`.replace(/\?+$/, '?');
  }
  return `What does the manual say about ${topic}?`;
}

function topicsFromChunk(chunk: ManualChunk): string[] {
  const topics = [cleanTopic(chunk.section_title)];

  for (const keyTerm of chunk.key_terms) {
    const topic = cleanTopic(keyTerm);
    if (topic.split(/\s+/).length > 1 || /^(app|boq|hope|noa|tec|toc|otm|rfq)$/i.test(topic)) {
      topics.push(topic);
    }
  }

  return topics.filter(isUsefulTopic);
}

function buildSuggestions(chunks: ManualChunk[]): ManualQuestionSuggestion[] {
  const suggestions = new Map<string, ManualQuestionSuggestion>();

  for (const chunk of chunks) {
    for (const topic of topicsFromChunk(chunk)) {
      const question = questionForTopic(topic);
      const key = question.toLocaleLowerCase();
      const previous = suggestions.get(key);
      const topicText = [question, chunk.section_title, ...chunk.key_terms]
        .join(' ')
        .toLocaleLowerCase();
      const searchText = [
        topicText,
        chunk.content,
      ].join(' ').toLocaleLowerCase();

      if (!previous) {
        suggestions.set(key, {
          question,
          page: chunk.page_number,
          topicText,
          searchText,
        });
      } else {
        previous.topicText += ` ${topicText}`;
        previous.searchText += ` ${searchText}`;
        previous.page = Math.min(previous.page, chunk.page_number);
      }
    }
  }

  return Array.from(suggestions.values()).sort(
    (a, b) => a.page - b.page || a.question.localeCompare(b.question),
  );
}

export const MANUAL_QUESTION_SUGGESTIONS = buildSuggestions(INITIAL_MANUAL_CHUNKS);

const SEARCH_STOP_WORDS = new Set([
  'a', 'about', 'an', 'and', 'are', 'as', 'at', 'be', 'can', 'do', 'for',
  'from', 'how', 'i', 'in', 'is', 'it', 'me', 'my', 'of', 'on', 'or',
  'please', 'say', 'the', 'this', 'to', 'what', 'with',
]);

export function searchManualQuestionSuggestions(
  query: string,
  suggestions: ManualQuestionSuggestion[] = MANUAL_QUESTION_SUGGESTIONS,
): ManualQuestionSuggestion[] {
  const normalizedQuery = query.trim().toLocaleLowerCase();
  if (!normalizedQuery) return [];

  const terms = normalizedQuery
    .split(/[^\p{L}\p{N}]+/u)
    .filter((term) => term.length > 1 && !SEARCH_STOP_WORDS.has(term));
  if (terms.length === 0) return [];

  return suggestions
    .map((suggestion) => {
      const text = suggestion.searchText;
      const textTokens = new Set(text.split(/[^\p{L}\p{N}]+/u));
      const topicText = suggestion.topicText;
      const topicTokens = new Set(topicText.split(/[^\p{L}\p{N}]+/u));
      const matchingTerms = terms.filter((term) =>
        textTokens.has(term) || (term.length >= 5 && Array.from(textTokens).some((token) => token.startsWith(term))),
      ).length;
      const matchingTopicTerms = terms.filter((term) =>
        topicTokens.has(term) || (term.length >= 5 && Array.from(topicTokens).some((token) => token.startsWith(term))),
      ).length;
      return {
        suggestion,
        matchingTerms,
        matchingTopicTerms,
        exactTopicPhrase: ` ${topicText} `.includes(` ${normalizedQuery} `),
        exactPhrase: ` ${text} `.includes(` ${normalizedQuery} `),
      };
    })
    .filter(({ matchingTerms }) => matchingTerms === terms.length)
    .sort((a, b) =>
      b.matchingTopicTerms - a.matchingTopicTerms ||
      Number(b.exactTopicPhrase) - Number(a.exactTopicPhrase) ||
      Number(b.exactPhrase) - Number(a.exactPhrase) ||
      b.matchingTerms - a.matchingTerms ||
      a.suggestion.page - b.suggestion.page,
    )
    .map(({ suggestion }) => suggestion);
}
