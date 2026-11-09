export function formatAssistantAnswer(text: string): string {
  const withoutBoilerplate = text
    .replace(/^\s*(?:📖\s*)?[*_]{0,2}Source\s*:.*$/gim, '')
    .replace(/^\s*📷\s*[*_]{0,2}Refer to portal screens?[*_]{0,2}\s*:.*$/gim, '')
    .replace(/^\s*#{1,6}\s*(?:📋\s*)?(?:Key Details|Answer|Response)\s*:?\s*$/gim, '')
    .replace(/^\s*📋\s*$/gm, '')
    .replace(/^Great question!\s*Here(?:'|’)s what the official e-GP manual says about [^:\n]+:\s*/i, '')
    .replace(/Would you like me to explain[^?\n]*\??[^\n]*/gi, '')
    .replace(/Let me know if you(?:'|’)d like[^.\n]*\.?/gi, '')
    .replace(/\*{0,2}\(?\s*pages?\s+\d+(?:\s*[-–—,]\s*\d+)*\s*\)?\*{0,2}/gi, '')
    .replace(/^\s*---+\s*$/gm, '');

  const lines = withoutBoilerplate
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const balancedBoldLines = lines.map((line) => {
    const boldMarkers = line.match(/\*\*/g) || [];
    if (boldMarkers.length % 2 === 0) return line;

    const unmatchedMarker = line.lastIndexOf('**');
    return `${line.slice(0, unmatchedMarker)}${line.slice(unmatchedMarker + 2)}`.trim();
  });
  const hadNumberedItems = balancedBoldLines.some((line) => /^(?:\*\*)?\d+(?:\.\d+)*[.)](?:\*\*)?\s+/.test(line));
  const cleanedLines = balancedBoldLines
    .map((line) => line
      .replace(/^Screen\s*[-–—:]\s*[A-Za-z0-9.]+\s+\d+(?:\.\d+)*\s*/i, '')
      .replace(/^Screen\s*[-–—:]\s*[A-Za-z0-9.]+\s*/i, '')
      .replace(/^\(?As shown in Screen\s*[-–—:]\s*[A-Za-z0-9.]+\)?[.!]?\s*$/i, '')
      .replace(/\s*\(?\s*Page\s+\d+(?:\s*[-–—,]\s*\d+)*\s*\)?/gi, '')
      .replace(/\s+within the login\.?$/i, '')
      .replace(/\s+/g, ' ')
      .replace(/^[^A-Za-z0-9]+/, '')
      .trim())
    .filter((line) => line.length > 0)
    .filter((line) => !/^This message signifies\b/i.test(line))
    .filter((line) => !/^[a-z]\s+Changed successfully/.test(line))
    .filter((line) => !/^\(?As shown in Screen\b/i.test(line));

  const uniqueLines = cleanedLines.filter((line, index) =>
    cleanedLines.findIndex((candidate) => candidate.toLowerCase() === line.toLowerCase()) === index
  );

  if (hadNumberedItems) {
    return uniqueLines.join('\n');
  }
  return uniqueLines.join('\n\n');
}
