from app.main import main

def test_main_prints(capsys):
    main()
    captured = capsys.readouterr()
    assert "App started" in captured.out
