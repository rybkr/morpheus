#!/usr/bin/env pwsh

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("codex", "claude", "custom")]
  [string]$Agent,

  [ValidateSet("user", "repo")]
  [string]$Scope = "user",

  [string[]]$Skill,
  [switch]$All,
  [string]$Target,
  [switch]$Force,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

function Resolve-TargetPath {
  if ($Target) { return $Target }

  switch ($Agent) {
    "codex" {
      if ($Scope -eq "repo") {
        return Join-Path $RepoRoot ".codex/skills"
      }

      if ($env:CODEX_HOME) {
        return Join-Path $env:CODEX_HOME "skills"
      }

      return Join-Path $HOME ".codex/skills"
    }
    "claude" {
      if ($Scope -eq "repo") {
        return Join-Path $RepoRoot ".claude/skills"
      }

      return Join-Path $HOME ".claude/skills"
    }
    "custom" {
      throw "custom agent requires -Target <path>"
    }
    default {
      throw "Unsupported agent '$Agent'"
    }
  }
}

function Discover-Skills {
  Get-ChildItem -Path $RepoRoot -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } |
    Select-Object -ExpandProperty Name |
    Sort-Object
}

if ($All) {
  $Skill = @(Discover-Skills)
}

if (-not $Skill -or $Skill.Count -eq 0) {
  throw "No skills selected. Use -All or one or more -Skill <name>."
}

$Destination = Resolve-TargetPath

Write-Host "Agent      : $Agent"
Write-Host "Scope      : $Scope"
Write-Host "Repository : $RepoRoot"
Write-Host "Target     : $Destination"
Write-Host "Dry run    : $DryRun"
Write-Host ""

$hadError = $false
foreach ($skillName in $Skill) {
  $sourcePath = Join-Path $RepoRoot $skillName
  $skillFile = Join-Path $sourcePath "SKILL.md"
  $destPath = Join-Path $Destination $skillName

  if (-not (Test-Path $skillFile)) {
    Write-Error "Skipping '$skillName': missing $skillFile"
    $hadError = $true
    continue
  }

  if ((Test-Path $destPath) -and -not $Force) {
    Write-Host "Skipping '$skillName': destination exists ($destPath). Use -Force to overwrite."
    continue
  }

  Write-Host "Installing $skillName -> $destPath"
  if ($DryRun) { continue }

  New-Item -ItemType Directory -Force -Path $Destination | Out-Null
  if (Test-Path $destPath) {
    Remove-Item -Recurse -Force -Path $destPath
  }
  Copy-Item -Recurse -Force -Path $sourcePath -Destination $destPath
}

if ($hadError) { exit 1 }
