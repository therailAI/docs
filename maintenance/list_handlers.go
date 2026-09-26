// List statically registered handler keys without importing service implementations.
package main

import (
	"encoding/json"
	"flag"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strconv"
)

func main() {
	root := flag.String("root", "", "implementation workspace")
	flag.Parse()
	out := map[string][]string{}
	files, err := filepath.Glob(filepath.Join(*root, "rail-*-api", "internal", "api", "handlers.go"))
	if err != nil {
		panic(err)
	}
	for _, path := range files {
		name := filepath.Base(filepath.Dir(filepath.Dir(filepath.Dir(path))))
		file, err := parser.ParseFile(token.NewFileSet(), path, nil, 0)
		if err != nil {
			panic(err)
		}
		ast.Inspect(file, func(n ast.Node) bool {
			literal, ok := n.(*ast.CompositeLit)
			if !ok {
				return true
			}
			typ, ok := literal.Type.(*ast.MapType)
			if !ok {
				return true
			}
			value, ok := typ.Value.(*ast.SelectorExpr)
			if !ok || value.Sel.Name != "Handler" {
				return true
			}
			pkg, ok := value.X.(*ast.Ident)
			if !ok || pkg.Name != "httpapi" {
				return true
			}
			for _, item := range literal.Elts {
				pair, ok := item.(*ast.KeyValueExpr)
				if !ok {
					panic("non-keyed handler entry")
				}
				key, ok := pair.Key.(*ast.BasicLit)
				if !ok {
					panic("nonliteral handler key")
				}
				id, err := strconv.Unquote(key.Value)
				if err != nil {
					panic(err)
				}
				out[name] = append(out[name], id)
			}
			return true
		})
	}
	if err := json.NewEncoder(os.Stdout).Encode(out); err != nil {
		panic(err)
	}
}
