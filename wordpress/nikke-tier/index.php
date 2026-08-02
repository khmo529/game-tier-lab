<?php
/**
 * Template Name: Nikke Tier
 * Description: 승리의 여신 NIKKE 전체 캐릭터 티어표 페이지 (GeneratePress Child Theme)
 *
 * 사용법:
 *  1) 이 파일을 테마 루트에 `page-nikke-tier.php` 로 복사 후 페이지 편집 화면에서 템플릿 선택
 *  2) 또는 functions.php 에서 아래 스니펫을 include 후 숏코드 [nikke_tier] 사용
 *
 * 이 템플릿은 GeneratePress 표준 훅(generate_before_content 등)을 그대로 사용합니다.
 */

if ( ! defined( 'ABSPATH' ) ) exit;

get_header();

// -----------------------------------------------------------------------------
// SEO: JSON-LD (Breadcrumb + FAQ) — 헤더에 인라인으로 출력
// -----------------------------------------------------------------------------
$page_url   = esc_url( home_url( add_query_arg( null, null ) ) );
$page_title = '승리의 여신 NIKKE 최신 캐릭터 티어표';
$page_desc  = '2026년 최신 메타 기준 NIKKE 전체 캐릭터 티어표. 스토리/보스/PVP/레이드/유니온 컨텐츠별 추천, 주간 변경사항, 오버로드/큐브/스킬 우선순위까지.';
?>
<meta name="description" content="<?php echo esc_attr( $page_desc ); ?>">
<meta property="og:type" content="article">
<meta property="og:title" content="<?php echo esc_attr( $page_title ); ?>">
<meta property="og:description" content="<?php echo esc_attr( $page_desc ); ?>">
<meta property="og:url" content="<?php echo $page_url; ?>">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="<?php echo esc_attr( $page_title ); ?>">
<meta name="twitter:description" content="<?php echo esc_attr( $page_desc ); ?>">
<link rel="canonical" href="<?php echo $page_url; ?>">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type":"ListItem","position":1,"name":"홈","item":"<?php echo esc_url( home_url('/') ); ?>"},
    {"@type":"ListItem","position":2,"name":"NIKKE 티어표","item":"<?php echo $page_url; ?>"}
  ]
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type":"Question","name":"NIKKE 티어표는 얼마나 자주 업데이트되나요?","acceptedAnswer":{"@type":"Answer","text":"매주 1회, 최신 메타를 반영해 업데이트됩니다."}},
    {"@type":"Question","name":"티어는 어떤 기준으로 정해지나요?","acceptedAnswer":{"@type":"Answer","text":"스토리·보스·PVP·레이드·유니온레이드 등 주요 컨텐츠에서의 활용도와 픽률을 종합해 SSS ~ C 등급으로 분류합니다."}},
    {"@type":"Question","name":"신규 캐릭터는 어디서 확인하나요?","acceptedAnswer":{"@type":"Answer","text":"페이지 상단 '주간 변경사항' 섹션과 캐릭터 카드의 NEW 배지로 확인할 수 있습니다."}}
  ]
}
</script>

<div id="nikke-tier-app" class="nikke-root" data-base="<?php echo esc_url( get_stylesheet_directory_uri() . '/nikke-tier' ); ?>">
  <?php // 앱 마운트 지점 — 실제 렌더링은 script.js 에서 수행 ?>
  <noscript>
    <p style="padding:20px;text-align:center">JavaScript를 활성화하면 티어표가 표시됩니다.</p>
  </noscript>
</div>

<?php
get_footer();
