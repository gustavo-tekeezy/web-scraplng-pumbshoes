.\venv\Scripts\activate
deactivate

docker-compose down
docker-compose up --build


docker ps
docker exec -it shopbot bash



# Regras fixas para ignorar
$exclude = @("venv", ".venv", ".git", "__pycache__", "node_modules", ".ipynb_checkpoints")

# Carrega .gitignore, se existir
$gitignore = Get-Content .gitignore -ErrorAction SilentlyContinue |
    Where-Object { $_ -and -not $_.StartsWith("#") }

function Show-Tree {
    param(
        [string]$Path,
        [string]$Prefix = ""
    )

    $items = Get-ChildItem $Path -Force | Sort-Object Name | Where-Object {
        $name = $_.Name

        # Ignora regras fixas
        if ($exclude -contains $name) { return $false }

        # Ignora padrões do .gitignore
        foreach ($rule in $gitignore) {
            if ($name -like $rule) { return $false }
        }

        return $true
    }

    for ($i = 0; $i -lt $items.Count; $i++) {
        $item = $items[$i]
        $isLast = ($i -eq $items.Count - 1)
        $connector = if ($isLast) { "└── " } else { "├── " }

        Write-Output "$Prefix$connector$($item.Name)"

        if ($item.PSIsContainer) {
            $newPrefix = if ($isLast) { "$Prefix    " } else { "$Prefix│   " }
            Show-Tree -Path $item.FullName -Prefix $newPrefix
        }
    }
}

Show-Tree "."
