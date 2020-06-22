from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        # Display this completion, black on yellow.
        # yield Completion('completion1', start_position=0,
        #                  style='bg:ansiyellow fg:ansiblack')

        # # Underline completion.
        # yield Completion('completion2', start_position=0,
        #                  style='underline')

        # # Specify class name, which will be looked up in the style sheet.
        # yield Completion('completion3', start_position=0,
        #                  style='class:special-completion')


        yield Completion('completion1', start_position=0,
                         style='bg:ansiyellow fg:ansiblack')



session = PromptSession()

while True:
    text = session.prompt('> ', auto_suggest=AutoSuggestFromHistory(), completer=my_completer, complete_while_typing=True)


