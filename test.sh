#!/bin/sh

export KEY="Tdya28QrbghAdvAQAyQKYq8Kh8aRfntUbvV1E1wMkm7e0h77a7i9YC1zqIt3D7eLL8SdHmdeIG6GlJmvmL5BW2piSPV1OQqorTXL68etEd3n26kf41ZSaBhtpoacBdNwQQhf8wE63sJ1ZMCSlerfQdnIdjzmv6Ngd6D90WKNAi9QiNZgcb0kEZMf8en2R26YfwJwzMIdT3EImZ9Q1o7MnQjY1sojHqL5p358a5jYGtOoAdrX6jVKcA7UTsec"

export HOST="http://localhost:8081/"
export API="key/create"
export URL="${HOST}${API}"

echo $URL

curl -X POST --data "key=$KEY&member_id=1&readonly=0&dba=0" $URL
