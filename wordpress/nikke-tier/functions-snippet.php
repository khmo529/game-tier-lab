<?php
/**
 * NIKKE Tier — GeneratePress Child Theme 등록 스니펫
 *
 * functions.php 안에서 아래처럼 include 하세요:
 *   require_once get_stylesheet_directory() . '/nikke-tier/functions-snippet.php';
 *
 * 제공 기능:
 *  - 에셋(CSS/JS) 자동 로딩 (해당 페이지에서만)
 *  - Pretendard 웹폰트 preconnect
 *  - 숏코드 [nikke_tier] 지원 → Gutenberg 블록 어디에나 삽입 가능
 */

if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * 에셋 등록.
 * 성능을 위해 실제로 사용되는 페이지(숏코드 or 페이지 템플릿)에서만 enqueue.
 */
function nikke_tier_register_assets() {
	$base = get_stylesheet_directory_uri() . '/nikke-tier';
	$ver  = @filemtime( get_stylesheet_directory() . '/nikke-tier/style.css' ) ?: '1.0.0';

	wp_register_style(
		'nikke-tier-style',
		$base . '/style.css',
		[],
		$ver
	);

	wp_register_script(
		'nikke-tier-script',
		$base . '/script.js',
		[],
		$ver,
		true // footer
	);

	// script.js 로 base URL 전달 (JSON/이미지 경로 계산용)
	wp_localize_script( 'nikke-tier-script', 'NIKKE_TIER_CFG', [
		'base'   => $base,
		'ajax'   => admin_url( 'admin-ajax.php' ),
		'locale' => get_locale(),
	] );
}
add_action( 'wp_enqueue_scripts', 'nikke_tier_register_assets' );

/**
 * Pretendard 웹폰트 preconnect (성능 최적화)
 */
function nikke_tier_head_hints() {
	echo '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>' . "\n";
	echo '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">' . "\n";
}
add_action( 'wp_head', 'nikke_tier_head_hints', 1 );

/**
 * 숏코드: [nikke_tier]
 */
function nikke_tier_shortcode( $atts = [] ) {
	wp_enqueue_style( 'nikke-tier-style' );
	wp_enqueue_script( 'nikke-tier-script' );

	$base = esc_url( get_stylesheet_directory_uri() . '/nikke-tier' );
	ob_start(); ?>
	<div id="nikke-tier-app" class="nikke-root" data-base="<?php echo $base; ?>">
		<noscript><p style="padding:20px;text-align:center">JavaScript를 활성화하면 티어표가 표시됩니다.</p></noscript>
	</div>
	<?php
	return ob_get_clean();
}
add_shortcode( 'nikke_tier', 'nikke_tier_shortcode' );

/**
 * 페이지 템플릿(page-nikke-tier.php)이 로드될 때도 에셋 enqueue.
 */
function nikke_tier_maybe_enqueue() {
	if ( is_page_template( 'page-nikke-tier.php' ) || is_page( 'nikke-tier' ) ) {
		wp_enqueue_style( 'nikke-tier-style' );
		wp_enqueue_script( 'nikke-tier-script' );
	}
}
add_action( 'wp_enqueue_scripts', 'nikke_tier_maybe_enqueue', 20 );
