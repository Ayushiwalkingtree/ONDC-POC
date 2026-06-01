# CURL Examples

Set `base_url` to your local or UAT Buyer NP URL before running these commands.

```powershell
$base_url = "http://127.0.0.1:8000"
```

## search

```powershell
curl -X POST "$base_url/ondc/search" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/search.json"
```

## on_search

```powershell
curl -X POST "$base_url/ondc/on_search" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_search.json"
```

## select

```powershell
curl -X POST "$base_url/ondc/select" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/select.json"
```

## on_select

```powershell
curl -X POST "$base_url/ondc/on_select" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_select.json"
```

## init

```powershell
curl -X POST "$base_url/ondc/init" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/init.json"
```

## on_init

```powershell
curl -X POST "$base_url/ondc/on_init" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_init.json"
```

## confirm

```powershell
curl -X POST "$base_url/ondc/confirm" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/confirm.json"
```

## on_confirm

```powershell
curl -X POST "$base_url/ondc/on_confirm" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_confirm.json"
```

## status

```powershell
curl -X POST "$base_url/ondc/status" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/status.json"
```

## on_status

```powershell
curl -X POST "$base_url/ondc/on_status" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_status.json"
```

## update

```powershell
curl -X POST "$base_url/ondc/update" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/update.json"
```

## on_update

```powershell
curl -X POST "$base_url/ondc/on_update" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_update.json"
```

## cancel

```powershell
curl -X POST "$base_url/ondc/cancel" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/cancel.json"
```

## on_cancel

```powershell
curl -X POST "$base_url/ondc/on_cancel" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_cancel.json"
```

## track

```powershell
curl -X POST "$base_url/ondc/track" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/track.json"
```

## on_track

```powershell
curl -X POST "$base_url/ondc/on_track" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_track.json"
```

## support

```powershell
curl -X POST "$base_url/ondc/support" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/support.json"
```

## on_support

```powershell
curl -X POST "$base_url/ondc/on_support" `
  -H "Content-Type: application/json" `
  --data-binary "@postman/payloads/on_support.json"
```
