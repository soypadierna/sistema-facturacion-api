ROLE_PERMISSIONS: dict[int, list[str]] = {
    1: ["dashboard", "clientes", "productos", "categorias", "facturas", "informes", "empleados", "roles", "crear-admin"],
    2: ["dashboard", "clientes", "facturas", "informes"],
    3: ["dashboard", "productos"],
    4: ["dashboard", "clientes", "productos", "categorias", "facturas", "informes"],
}