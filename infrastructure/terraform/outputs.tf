output "s3_media_bucket" {
  value = aws_s3_bucket.media_storage.id
}

output "s3_cdn_bucket" {
  value = aws_s3_bucket.cdn_storage.id
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.cdn.id
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.cdn.domain_name
}
