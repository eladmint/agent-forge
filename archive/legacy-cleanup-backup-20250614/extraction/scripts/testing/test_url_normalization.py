#!/usr/bin/env python3
"""
Test URL Normalization and Redirect Following
Demonstrates the new URL utilities functionality
"""

from agent_forge.core.shared.url_utils import (
    are_urls_equivalent,
    extract_luma_id,
    follow_redirects_enhanced,
    get_canonical_url,
    normalize_url_enhanced,
)


def test_url_normalization():
    """Test URL normalization functionality"""

    print("🔗 Testing URL Normalization and Redirect Following\n")

    # Test cases
    test_urls = [
        "https://lu.ma/kuhtg0fx",  # EthCC Red Team redirect URL
        "https://lu.ma/lz5z7jhb",  # Direct Red Team URL
        "https://lu.ma/DeFAIBreakfast?utm_source=twitter&utm_campaign=test",
        "https://lu.ma/event/evt-123?ref=social&fbclid=abc123",
    ]

    print("📝 URL Normalization Tests:")
    for url in test_urls:
        normalized = normalize_url_enhanced(url)
        print(f"  Original:   {url}")
        print(f"  Normalized: {normalized}")
        print()

    print("🔄 Redirect Following Tests:")
    for url in test_urls[:2]:  # Only test redirect URLs
        try:
            final_url, redirect_chain = follow_redirects_enhanced(url)
            print(f"  Original: {url}")
            print(f"  Final:    {final_url}")
            if redirect_chain:
                print(f"  Chain:    {' -> '.join(redirect_chain)}")
            print()
        except Exception as e:
            print(f"  Error for {url}: {e}")
            print()

    print("🆔 Luma ID Extraction Tests:")
    for url in test_urls:
        luma_id = extract_luma_id(url)
        print(f"  URL: {url}")
        print(f"  ID:  {luma_id}")
        print()

    print("🔍 URL Equivalence Tests:")
    # Test if the EthCC redirect URLs are equivalent
    ethcc_redirect = "https://lu.ma/kuhtg0fx"
    ethcc_direct = "https://lu.ma/lz5z7jhb"

    equivalent = are_urls_equivalent(ethcc_redirect, ethcc_direct)
    print(f"  {ethcc_redirect}")
    print(f"  {ethcc_direct}")
    print(f"  Equivalent: {equivalent}")
    print()

    # Test canonical URL resolution
    print("🎯 Canonical URL Resolution:")
    for url in test_urls:
        canonical = get_canonical_url(url)
        print(f"  Original:  {url}")
        print(f"  Canonical: {canonical}")
        print()


def test_extraction_pipeline_integration():
    """Test how this would integrate with the extraction pipeline"""

    print("🔧 Extraction Pipeline Integration Test\n")

    # Simulate finding these URLs during extraction
    discovered_urls = [
        "https://lu.ma/kuhtg0fx",  # Redirect URL from EthCC page
        "https://lu.ma/lz5z7jhb",  # Same event, direct URL
        "https://lu.ma/DeFAIBreakfast?utm_source=ethcc",  # With tracking
        "https://lu.ma/DeFAIBreakfast",  # Clean version
    ]

    print("📊 Deduplication Simulation:")
    canonical_urls = {}
    for url in discovered_urls:
        canonical = get_canonical_url(url)
        if canonical not in canonical_urls:
            canonical_urls[canonical] = []
        canonical_urls[canonical].append(url)

    for canonical, variants in canonical_urls.items():
        print(f"  Canonical: {canonical}")
        for variant in variants:
            print(f"    Variant: {variant}")
        print()

    print(
        f"✅ Reduced {len(discovered_urls)} URLs to {len(canonical_urls)} unique events"
    )


if __name__ == "__main__":
    test_url_normalization()
    print("=" * 50)
    test_extraction_pipeline_integration()
