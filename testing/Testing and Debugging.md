
To test or debug your application files and decorated functions, you will need to provide the Chainlit context to your test suite. 

In your main application script or test files add:

```
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
```

Then run the script from your IDE in debug mode. 