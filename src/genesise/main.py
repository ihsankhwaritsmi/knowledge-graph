import typer
from .commands import init, sync, lint, list_nodes, flag_stale, verify, rename, summary, gap_fill

app = typer.Typer(
    name="gns",
    help="Genesise — deterministic CLI for your AI-maintained local knowledge graph.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

app.command("init")(init.run)
app.command("sync")(sync.run)
app.command("lint")(lint.run)
app.command("list")(list_nodes.run)
app.command("summary")(summary.run)
app.command("flag-stale")(flag_stale.run)
app.command("verify")(verify.run)
app.command("rename")(rename.run)
app.command("gap-fill")(gap_fill.run)

if __name__ == "__main__":
    app()
