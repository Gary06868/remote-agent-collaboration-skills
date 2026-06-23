param(
  [ValidateSet("user", "project")]
  [string]$Scope = "user",
  [string]$Target = ""
)

$argsList = @("tools/install.py", "--scope", $Scope)
if ($Target -ne "") {
  $argsList += @("--target", $Target)
}
py -3 @argsList
