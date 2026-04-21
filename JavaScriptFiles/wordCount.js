function wordCount(str) {
  const words = str.trim().split(/\s+/);
  const result = {};
  for (const word of words) {
    if(result[word]) {
      result[word]++;
    }else {
      result[word] = 1;
    }
  }
  return result;
}
console.log(wordCount("hello world hello"));    