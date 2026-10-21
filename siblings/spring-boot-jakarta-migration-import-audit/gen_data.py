import os
import random

random.seed(4217)

MIG = [
    "javax.persistence.Entity", "javax.persistence.Id", "javax.persistence.Table",
    "javax.persistence.Column", "javax.persistence.GeneratedValue", "javax.persistence.*",
    "javax.validation.Valid", "javax.validation.constraints.NotNull",
    "javax.validation.constraints.Email", "javax.validation.constraints.Size",
    "javax.servlet.http.HttpServletRequest", "javax.servlet.Filter", "javax.servlet.FilterChain",
    "javax.annotation.PostConstruct", "javax.annotation.PreDestroy", "javax.annotation.Resource",
    "javax.annotation.Priority", "javax.transaction.Transactional",
    "javax.xml.bind.annotation.XmlRootElement", "javax.ws.rs.core.Response",
    "javax.mail.Session", "javax.jms.Queue",
]
STAY = [
    "javax.sql.DataSource", "javax.crypto.Cipher", "javax.crypto.spec.SecretKeySpec",
    "javax.net.ssl.SSLContext", "javax.annotation.processing.Generated",
    "javax.management.MBeanServer", "javax.transaction.xa.XAResource",
    "javax.naming.InitialContext",
]
STATIC = [
    "static javax.persistence.GenerationType.IDENTITY",
    "static javax.persistence.CascadeType.ALL",
    "static javax.crypto.Cipher.ENCRYPT_MODE",
]
OTHER = [
    "java.util.List", "java.util.Map", "java.time.LocalDateTime",
    "org.springframework.stereotype.Service",
    "org.springframework.web.bind.annotation.RestController",
    "org.hibernate.annotations.CreationTimestamp",
]

FILES = [
    ("main", "model", "User"), ("main", "model", "Order"),
    ("main", "dto", "CreateUserRequest"), ("main", "dto", "OrderDto"),
    ("main", "web", "UserController"), ("main", "web", "AuthFilter"),
    ("main", "service", "UserService"), ("main", "service", "CryptoService"),
    ("main", "service", "MailService"), ("main", "config", "DataConfig"),
    ("main", "config", "XaConfig"), ("main", "repository", "UserRepository"),
    ("main", "util", "Tokens"), ("test", "service", "UserServiceTest"),
    ("test", "web", "AuthFilterTest"),
]

for base, pkg, name in FILES:
    imps = random.sample(MIG, random.randint(0, 6))
    imps += random.sample(STAY, random.randint(0, 2))
    imps += random.sample(OTHER, random.randint(1, 3))
    if random.random() < 0.4:
        imps.append(random.choice(STATIC))
    random.shuffle(imps)
    lines = [f"package com.example.app.{pkg};", ""]
    for i in imps:
        indent = "  " if random.random() < 0.15 else ""
        lines.append(f"{indent}import {i};")
    lines.append("")
    if random.random() < 0.5:
        lines.append("// import javax.persistence.Version; (legacy, removed)")
    lines += [
        "/**",
        f" * {name} component.",
        " * import javax.servlet.ServletException;",
        " */",
        f"public class {name} {{",
        '    private static final String NOTE = "javax.persistence is legacy";',
        "}",
        "",
    ]
    d = os.path.join("src", base, "java", "com", "example", "app", pkg)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".java"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

with open(os.path.join("src", "README.txt"), "w", encoding="utf-8") as f:
    f.write("Notes\nimport javax.persistence.Entity;\nimport javax.servlet.Filter;\n")
with open(os.path.join("src", "main", "java", "com", "example", "app", "model", "User.java.bak"), "w", encoding="utf-8") as f:
    f.write("package x;\nimport javax.validation.Valid;\n")
