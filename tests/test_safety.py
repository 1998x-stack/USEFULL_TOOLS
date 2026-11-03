"""Regression tests for destructive file operations and prompt paths."""

import pytest

from devkit.files.dedup import find_duplicates, remove_duplicates
from devkit.files.batch_rename import batch_rename
from devkit.ai.prompt_template import save_template, load_template, list_templates, render_template


def test_numbered_file_with_different_content_is_never_deleted(tmp_path):
    (tmp_path / 'record.txt').write_text('ABCDEFGH')
    (tmp_path / 'record (1).txt').write_text('abcdefgh')
    assert find_duplicates(str(tmp_path), ['*.txt']) == []
    assert remove_duplicates(str(tmp_path), ['*.txt'], dry_run=False) == []
    assert (tmp_path / 'record (1).txt').read_text() == 'abcdefgh'


def test_identical_numbered_copy_is_removed(tmp_path):
    (tmp_path / 'record.txt').write_bytes(b'abc' * 1000)
    (tmp_path / 'record (1).txt').write_bytes(b'abc' * 1000)
    candidates = find_duplicates(str(tmp_path), ['*.txt'])
    assert candidates == [str(tmp_path / 'record (1).txt')]
    assert remove_duplicates(str(tmp_path), ['*.txt']) == candidates
    assert (tmp_path / 'record (1).txt').exists()
    assert remove_duplicates(str(tmp_path), ['*.txt'], dry_run=False) == candidates
    assert (tmp_path / 'record.txt').exists()
    assert not (tmp_path / 'record (1).txt').exists()


def test_symlink_is_never_removed(tmp_path):
    (tmp_path / 'record.txt').write_text('same')
    try:
        (tmp_path / 'record (1).txt').symlink_to(tmp_path / 'record.txt')
    except (OSError, NotImplementedError):
        pytest.skip('symlinks not available')
    assert remove_duplicates(str(tmp_path), ['*.txt'], dry_run=False) == []
    assert (tmp_path / 'record (1).txt').is_symlink()


def test_rename_rejects_existing_destination_and_keeps_all_contents(tmp_path):
    (tmp_path / 'a.txt').write_text('A')
    (tmp_path / 'b.jpg').write_text('B')
    (tmp_path / 'img_01.jpg').write_text('KEEP')
    with pytest.raises(FileExistsError):
        batch_rename(str(tmp_path), 'img_{n:02d}.jpg', filter_ext='txt', dry_run=False)
    assert (tmp_path / 'a.txt').read_text() == 'A'
    assert (tmp_path / 'img_01.jpg').read_text() == 'KEEP'
    assert (tmp_path / 'b.jpg').read_text() == 'B'


def test_rename_rejects_path_traversal(tmp_path):
    (tmp_path / 'a.txt').write_text('A')
    with pytest.raises(ValueError):
        batch_rename(str(tmp_path), '../outside_{n}.txt', dry_run=False)
    assert (tmp_path / 'a.txt').exists()


def test_rename_rejects_duplicate_targets(tmp_path):
    (tmp_path / 'a.txt').write_text('A')
    (tmp_path / 'b.txt').write_text('B')
    with pytest.raises(FileExistsError):
        batch_rename(str(tmp_path), 'same.txt', dry_run=False)
    assert (tmp_path / 'a.txt').read_text() == 'A'
    assert (tmp_path / 'b.txt').read_text() == 'B'


def test_rename_staging_preserves_content(tmp_path):
    (tmp_path / 'a.txt').write_text('A')
    (tmp_path / 'b.txt').write_text('B')
    result = batch_rename(str(tmp_path), 'file_{n:02d}.txt', dry_run=False)
    assert len(result) == 2
    assert (tmp_path / 'file_01.txt').read_text() == 'A'
    assert (tmp_path / 'file_02.txt').read_text() == 'B'
    assert not any(p.name.startswith('.devkit-rename-') for p in tmp_path.iterdir())


def test_template_rejects_traversal(tmp_path):
    for name in ('../outside', 'nested/file', '..', '/tmp/escape'):
        with pytest.raises(ValueError):
            save_template(name, 'secret', str(tmp_path))
        with pytest.raises(ValueError):
            load_template(name, str(tmp_path))


def test_template_symlink_is_rejected(tmp_path):
    outside = tmp_path / 'outside.txt'
    outside.write_text('keep')
    folder = tmp_path / 'prompts'
    folder.mkdir()
    try:
        (folder / 'unsafe.txt').symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip('symlinks not available')
    with pytest.raises(ValueError):
        save_template('unsafe', 'broken', str(folder))
    with pytest.raises(ValueError):
        load_template('unsafe', str(folder))
    assert outside.read_text() == 'keep'


def test_valid_templates_and_jinja(tmp_path):
    save_template('test_01', 'hello', str(tmp_path))
    assert load_template('test_01', str(tmp_path)) == 'hello'
    assert list_templates(str(tmp_path)) == ['test_01']
    assert render_template('{{ name }}', {'name': 'Alice'}) == 'Alice'


def test_rename_rollback_on_second_destination_failure(tmp_path, monkeypatch):
    import importlib
    module = importlib.import_module('devkit.files.batch_rename')
    (tmp_path / 'a.txt').write_text('A')
    (tmp_path / 'b.txt').write_text('B')
    original_rename = module.os.rename

    def fail_once(source, destination):
        if str(source).split('/')[-1].startswith('.devkit-rename-') and str(destination).endswith('file_02.txt'):
            raise OSError('injected final rename failure')
        return original_rename(source, destination)

    monkeypatch.setattr(module.os, 'rename', fail_once)
    with pytest.raises(OSError, match='injected'):
        module.batch_rename(str(tmp_path), 'file_{n:02d}.txt', dry_run=False)
    assert (tmp_path / 'a.txt').read_text() == 'A'
    assert (tmp_path / 'b.txt').read_text() == 'B'
    assert not any(p.name.startswith('.devkit-rename-') for p in tmp_path.iterdir())
