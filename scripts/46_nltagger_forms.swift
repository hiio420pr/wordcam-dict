import Foundation
import NaturalLanguage
// forms.tsv 의 꼴마다 NLTagger lemma(낱말 홀로)를 구해, 우리 표제어와 같으면 '규칙으로 됨' → 빼도 되는 목록에 쓴다
let a = CommandLine.arguments
let lang = NLLanguage(rawValue: a[1]); let path = a[2]; let outp = a[3]
let text = try! String(contentsOfFile: path, encoding: .utf8)
var drop: [String] = []; var n = 0, same = 0
let tg = NLTagger(tagSchemes: [.lemma])
print("available", NLTagger.availableTagSchemes(for: .word, language: lang).map(\.rawValue))
for line in text.split(separator: "\n") {
    let p = line.split(separator: "\t"); guard p.count == 2 else { continue }
    let f = String(p[0]); let hs = p[1].split(separator: "|").map(String.init)
    n += 1
    tg.string = f; tg.setLanguage(lang, range: f.startIndex..<f.endIndex)
    let (t, _) = tg.tag(at: f.startIndex, unit: .word, scheme: .lemma)
    if let l = t?.rawValue, hs.count == 1, l == hs[0] || l.lowercased() == hs[0].lowercased() { same += 1; drop.append(f) }
}
try! drop.joined(separator: "\n").write(toFile: outp, atomically: true, encoding: .utf8)
print(a[1], "forms", n, "nltagger-same", same)
