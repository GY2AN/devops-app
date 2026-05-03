# Run this after every laptop restart or when pods show ImagePullBackOff
$token = aws ecr get-login-password --region ap-south-1
kubectl delete secret ecr-pull-secret -n production --ignore-not-found
kubectl create secret docker-registry ecr-pull-secret `
  --namespace production `
  --docker-server=532549085896.dkr.ecr.ap-south-1.amazonaws.com `
  --docker-username=AWS `
  --docker-password=$token
kubectl delete pods -n production --all
Write-Host "ECR secret refreshed. Pods restarting..." -ForegroundColor Green
