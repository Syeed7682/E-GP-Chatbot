import { INITIAL_MANUAL_CHUNKS } from '../data/manualChunks';
import { ManualChunk } from '../types/egp';

export interface ManualQuestionSuggestion {
  question: string;
  page: number;
  topicText: string;
  searchText: string;
}

const GENERIC_TOPICS = new Set([
  'action',
  'admin',
  'after',
  'also',
  'answer',
  'available',
  'button',
  'change',
  'click',
  'created',
  'current',
  'details',
  'document',
  'enter',
  'following',
  'information',
  'input',
  'introduction',
  'item',
  'list',
  'overview',
  'page',
  'process',
  'procedure',
  'required',
  'screen',
  'select',
  'step',
  'steps',
  'system',
  'user',
  'updated',
  'using',
  'view',
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
    if (topic.split(/\s+/).length <= 3) {
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
        chunk.content.slice(0, 400),
      ].join(' ').toLocaleLowerCase();

      if (!previous) {
        suggestions.set(key, {
          question,
          page: chunk.page_number,
          topicText,
          searchText,
        });
      } else {
        if (previous.topicText.length < 1200) {
          previous.topicText = `${previous.topicText} ${topicText}`.slice(0, 1200);
        }
        if (previous.searchText.length < 2400) {
          previous.searchText = `${previous.searchText} ${searchText}`.slice(0, 2400);
        }
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

function isWithinOneEdit(query: string, candidate: string): boolean {
  if (Math.abs(query.length - candidate.length) > 1) return false;

  let queryIndex = 0;
  let candidateIndex = 0;
  let edits = 0;

  while (queryIndex < query.length && candidateIndex < candidate.length) {
    if (query[queryIndex] === candidate[candidateIndex]) {
      queryIndex += 1;
      candidateIndex += 1;
      continue;
    }

    edits += 1;
    if (edits > 1) return false;

    if (query.length > candidate.length) queryIndex += 1;
    else if (candidate.length > query.length) candidateIndex += 1;
    else {
      queryIndex += 1;
      candidateIndex += 1;
    }
  }

  return edits + Number(queryIndex < query.length || candidateIndex < candidate.length) <= 1;
}

function termMatchesTokens(term: string, tokens: Set<string>): boolean {
  for (const token of tokens) {
    if (token === term || (term.length >= 2 && token.startsWith(term))) return true;

    if (term.length >= 5) {
      const prefixLengths = [term.length - 1, term.length, term.length + 1];
      if (prefixLengths.some((length) =>
        length > 0 &&
        length <= token.length &&
        isWithinOneEdit(term, token.slice(0, length)),
      )) {
        return true;
      }
    }
  }

  return false;
}

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
      const questionTokens = new Set(suggestion.question.toLocaleLowerCase().split(/[^\p{L}\p{N}]+/u));
      const matchingTerms = terms.filter((term) => termMatchesTokens(term, textTokens)).length;
      const matchingTopicTerms = terms.filter((term) => termMatchesTokens(term, topicTokens)).length;
      const matchingQuestionTerms = terms.filter((term) => termMatchesTokens(term, questionTokens)).length;
      return {
        suggestion,
        matchingTerms,
        matchingTopicTerms,
        matchingQuestionTerms,
        exactTopicPhrase: ` ${topicText} `.includes(` ${normalizedQuery} `),
        exactPhrase: ` ${text} `.includes(` ${normalizedQuery} `),
      };
    })
    .filter(({ matchingTerms }) => matchingTerms === terms.length)
    .sort((a, b) =>
      b.matchingQuestionTerms - a.matchingQuestionTerms ||
      b.matchingTopicTerms - a.matchingTopicTerms ||
      Number(b.exactTopicPhrase) - Number(a.exactTopicPhrase) ||
      Number(b.exactPhrase) - Number(a.exactPhrase) ||
      b.matchingTerms - a.matchingTerms ||
      a.suggestion.page - b.suggestion.page,
    )
    .map(({ suggestion }) => suggestion);
}
