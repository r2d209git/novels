#!/usr/bin/env bash
# 장별 분량·대사 비율·절 수·제목 형식·금지어 검사.
# 사용법: check.sh <작품 폴더> [금지어 패턴 파일]
#   예: check.sh 장천무극
# 환경 변수 TARGET(기본 35000자), TOLERANCE(기본 10%)로 분량 기준을 바꾼다.
# 문제가 하나라도 있으면 종료 코드 1.
set -euo pipefail
# GNU grep 3.x는 en_US.UTF-8에서 [가-힣] 범위를 'Invalid collation'으로 거부한다. C.UTF-8은 코드포인트 순으로 처리한다.
export LC_ALL=C.UTF-8

work="${1:?작품 폴더를 지정하세요}"
skill_dir="$(cd "$(dirname "$0")/.." && pwd)"
banned="${2:-$skill_dir/presets/wuxia.banned}"
target="${TARGET:-35000}"
tol="${TOLERANCE:-10}"
lo=$(( target * (100 - tol) / 100 ))
hi=$(( target * (100 + tol) / 100 ))

chapters="$work/chapters"
[[ -d "$chapters" ]] || { echo "없음: $chapters" >&2; exit 1; }

status=0
printf '%-6s %7s %5s %3s  %s\n' 장 글자수 대사% 절 판정
for f in "$chapters"/[0-9][0-9].md; do
  chars=$(wc -m < "$f")
  dialog=$( (grep -oE '"[^"]*"|“[^”]*”' "$f" || true) | wc -m)
  sections=$(grep -c '^## ' "$f" || true)
  verdict=OK
  if (( chars < lo || chars > hi )); then verdict="분량 범위 밖($lo~$hi)"; status=1; fi
  if ! head -1 "$f" | grep -q '^# 제[0-9]*장 '; then verdict="$verdict, 제목 형식"; status=1; fi
  printf '%-6s %7d %4d%% %3d  %s\n' "$(basename "$f" .md)" "$chars" $(( dialog * 100 / chars )) "$sections" "$verdict"
done

echo "--- 금지어 ($(basename "$banned"))"
if [[ ! -f "$banned" ]]; then
  echo "금지어 파일 없음, 건너뜀"
  exit $status
fi
# 패턴 파일: 한 줄에 확장 정규식 하나. '#'은 주석, '!'로 시작하면 오탐 제외 패턴.
pattern=$(grep -vE '^(#|!|$)' "$banned" | paste -sd'|')
exclude=$(grep -E '^!' "$banned" | cut -c2- | paste -sd'|' || true)
rc=0
hits=$(grep -HnoE "$pattern" "$chapters"/[0-9][0-9].md) || rc=$?
if (( rc > 1 )); then
  echo "금지어 검사 실패: grep 오류(종료 코드 $rc). 패턴 파일을 확인하세요." >&2
  exit 2
fi
if [[ -n "$exclude" && -n "$hits" ]]; then
  hits=$(grep -vE "$exclude" <<<"$hits" || true)
fi
if [[ -n "$hits" ]]; then
  echo "$hits"
  status=1
else
  echo "없음"
fi
exit $status
