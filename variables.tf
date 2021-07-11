variable "var1" {
  default = "string1"
}
variable "var2" {
  default = "1"
}
variable "var3" {
  default = "True"
}
output "result" {
  value = var.var1
}
output "result2" {
  value = var.var2
}
output "result3" {
  value = var.var3
}