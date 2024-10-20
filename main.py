import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.core.window import Window
import pandas as pd
import matplotlib.pyplot as plt

import io
import contextlib

# Load the .kv file
Builder.load_file('gui.kv')


class PandasApp(BoxLayout):
    df = None  # Placeholder for the dataframe

    def load_data(self):
        # Open file chooser to load a CSV/Excel file
        content = FileChooserIconView(on_submit=self.select_file)
        popup = Popup(title="Open File", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def select_file(self, file_path, *args):
        file_path = file_path.selection[0]  # Get the first selected file
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(file_path)
                self.show_popup("Success", "Data loaded successfully!")
                self.populate_columns()
            except Exception as e:
                self.show_popup("Error", f"Failed to load data: {e}")

    def populate_columns(self):
        if self.df is not None:
            columns = ['None'] + list(self.df.columns)
            self.ids.filter_column.values = columns
            self.ids.group_column.values = columns
            self.ids.x_column.values = self.df.columns
            self.ids.y_column.values = self.df.columns

    def show_head(self):
        if self.df is not None:
            self.display_data(self.df.head(10))

    def show_info(self):
        if self.df is not None:
            # Create a popup to show the DataFrame info
            popup = Popup(title='Data Information', size_hint=(0.9, 0.9))

            # Create a GridLayout for the table
            layout = GridLayout(cols=3, padding=10, spacing=10)

            # Add headers
            layout.add_widget(Label(text='Column', bold=True))
            layout.add_widget(Label(text='Non-Null Count', bold=True))
            layout.add_widget(Label(text='Dtype', bold=True))

            # Get DataFrame info
            info_dict = {
                'Column': [],
                'Non-Null Count': [],
                'Dtype': []
            }

            # Collect data from DataFrame info
            for col in self.df.columns:
                info_dict['Column'].append(col)
                info_dict['Non-Null Count'].append(f"{self.df[col].count()} non-null")
                info_dict['Dtype'].append(str(self.df[col].dtype))

            # Fill in the data into the layout
            for i in range(len(info_dict['Column'])):
                layout.add_widget(Label(text=info_dict['Column'][i]))
                layout.add_widget(Label(text=info_dict['Non-Null Count'][i]))
                layout.add_widget(Label(text=info_dict['Dtype'][i]))

            # Wrap layout in ScrollView for scrolling capability
            scroll_view = ScrollView(size_hint=(1, 1))
            scroll_view.add_widget(layout)

            # Add scroll_view to popup
            popup.content = scroll_view
            popup.open()

    def show_describe(self):
        if self.df is not None:
            describe_df = self.df.describe()
            popup = Popup(title='Data Description', size_hint=(0.9, 0.9))

            # Create a BoxLayout to allow for horizontal and vertical scrolling
            layout = GridLayout(cols=len(describe_df.columns) + 2,
                                padding=10, spacing=10, size_hint_y=None)
            layout.bind(minimum_height=layout.setter(
                'height'))  # Enable dynamic height

            # Add the header for 'Statistic'
            layout.add_widget(Label(text='Statistic', bold=True,
                            size_hint_y=None, height=30))

            # Add headers for each column in the DataFrame
            for col in describe_df.columns:
                layout.add_widget(
                    Label(text=col, bold=True, size_hint_y=None, height=30))

            # Fill in the data into the layout with index for each row
            for idx, row in describe_df.iterrows():
                # Add the index label for the statistic (e.g., count, mean, std, etc.)
                layout.add_widget(
                    Label(text=str(idx), size_hint_y=None, height=30))

                # Add each value in the row to the layout
                for value in row:
                    layout.add_widget(Label(text=f"{value:.2f}" if isinstance(value, (int, float)) else str(value),
                                            size_hint_y=None, height=30))

                # Spacer for better readability
                # Spacer between rows
                layout.add_widget(Label(size_hint_y=None, height=10))

            # Wrap the layout in a ScrollView for scrolling capability
            scroll_view = ScrollView(size_hint=(
                1, 1), do_scroll_x=True, do_scroll_y=True)
            scroll_view.add_widget(layout)

            # Add scroll_view to the popup
            popup.content = scroll_view
            popup.open()



    def show_null_counts(self):
        if self.df is not None:
            null_counts = self.df.isnull().sum()
            null_counts_str = str(null_counts)
            self.show_popup("Null Value Counts", null_counts_str)

    def show_full_data(self):
        if self.df is not None:
            self.display_data(self.df)
    
    def validate_dataframe(self):
        if self.df is None or self.df.empty:
            self.display_message("Error", "No data loaded or the data is empty!")
            return False
        return True

    def apply_filter(self):
        if not self.validate_dataframe():
            return
        if self.df is not None:
            column = self.ids.filter_column.text
            value = self.ids.filter_value.text
            if column and value:
                filtered_df = self.df[self.df[column] == value]
                self.display_data(filtered_df)

    def sort_data(self):
        if self.df is not None:
            sorted_df = self.df.sort_values(by=self.df.columns[0])
            self.display_data(sorted_df)

    def drop_na(self):
        if self.df is not None:
            cleaned_df = self.df.dropna()
            self.display_data(cleaned_df)

    def fill_na(self):
        if self.df is not None:
            filled_df = self.df.fillna(0)  # Filling NA with 0, can be modified
            self.display_data(filled_df)

    def remove_duplicates(self):
        if self.df is not None:
            deduplicated_df = self.df.drop_duplicates()
            self.display_data(deduplicated_df)

    def apply_grouping(self):
        if self.df is not None:
            column = self.ids.group_column.text
            agg_func = self.ids.agg_function.text
            if column and agg_func:
                grouped_df = self.df.groupby(
                    column).agg(agg_func).reset_index()
                self.display_data(grouped_df)

    def plot_data(self):
        if not self.validate_dataframe():
            return
        if self.df is not None:
            plot_type = self.ids.plot_type.text
            x_column = self.ids.x_column.text
            y_column = self.ids.y_column.text
            if plot_type == 'line':
                self.df.plot(x=x_column, y=y_column, kind='line')
            elif plot_type == 'bar':
                self.df.plot(x=x_column, y=y_column, kind='bar')
            elif plot_type == 'hist':
                self.df[y_column].plot(kind='hist')
            elif plot_type == 'scatter':
                self.df.plot(x=x_column, y=y_column, kind='scatter')
            plt.show()

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(
            text=message), size_hint=(0.8, 0.8))
        popup.open()

    def display_data(self, data):
        # Clear previous data
        self.ids.data_grid.clear_widgets()

        if isinstance(data, pd.DataFrame):
            # Add column headers
            for column in data.columns:
                header = Label(text=column, bold=True,
                               size_hint_y=None, height='40dp')
                self.ids.data_grid.add_widget(header)

            # Add data rows
            for index, row in data.iterrows():
                for value in row:
                    button = Button(text=str(value), size_hint_x=None, width=100)
                    button.bind(on_press=lambda btn,
                                row=row: self.on_row_click(row))
                    self.ids.data_grid.add_widget(button)

            # Update the number of columns dynamically
            # Set the number of columns
            self.ids.data_grid.cols = len(data.columns)


    def export_data(self):
        if self.df is not None:
            content = FileChooserIconView(on_submit=self.save_file)
            popup = Popup(title="Save File", content=content,
                          size_hint=(0.9, 0.9))
            popup.open()

    def save_file(self, instance, file_path):
        file_path = file_path[0]
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.df.to_excel(file_path, index=False)
                self.show_popup("Success", "Data exported successfully!")
            except Exception as e:
                self.show_popup("Error", f"Failed to export data: {e}")


class PandasAppMain(App):
    def build(self):
        return PandasApp()


if __name__ == '__main__':
    PandasAppMain().run()
