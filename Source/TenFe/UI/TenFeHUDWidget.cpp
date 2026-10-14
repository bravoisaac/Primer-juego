#include "UI/TenFeHUDWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Character/TenFeCharacter.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ProgressBar.h"
#include "Components/Spacer.h"
#include "Components/TenFeEquipmentComponent.h"
#include "Components/TenFeStatsComponent.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

void UTenFeHUDWidget::SetCharacter(ATenFeCharacter* InCharacter)
{
    Character = InCharacter;
    Refresh();
}

void UTenFeHUDWidget::NativeConstruct()
{
    Super::NativeConstruct();
    BuildLayout();
    Refresh();
}

void UTenFeHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    Refresh();
}

void UTenFeHUDWidget::BuildLayout()
{
    if (WidgetTree->RootWidget)
    {
        return;
    }

    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("HUDRoot"));
    WidgetTree->RootWidget = Root;

    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("StatsPanel"));
    Panel->SetBrushColor(FLinearColor(0.015f, 0.018f, 0.025f, 0.82f));
    Panel->SetPadding(FMargin(14.0f));
    UCanvasPanelSlot* PanelSlot = Root->AddChildToCanvas(Panel);
    PanelSlot->SetPosition(FVector2D(28.0f, 28.0f));
    PanelSlot->SetSize(FVector2D(390.0f, 150.0f));

    UVerticalBox* Stack = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("StatsStack"));
    Panel->SetContent(Stack);

    UTextBlock* Title = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("GameTitle"));
    Title->SetText(FText::FromString(TEXT("TEN FE")));
    Title->SetColorAndOpacity(FSlateColor(FLinearColor(0.9f, 0.72f, 0.32f)));
    Title->SetFont(FSlateFontInfo(Title->GetFont().FontObject, 22));
    Stack->AddChildToVerticalBox(Title);

    HealthBar = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), TEXT("HealthBar"));
    HealthBar->SetFillColorAndOpacity(FLinearColor(0.68f, 0.04f, 0.06f, 1.0f));
    Stack->AddChildToVerticalBox(HealthBar)->SetPadding(FMargin(0.0f, 8.0f, 0.0f, 4.0f));

    StaminaBar = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), TEXT("StaminaBar"));
    StaminaBar->SetFillColorAndOpacity(FLinearColor(0.12f, 0.55f, 0.22f, 1.0f));
    Stack->AddChildToVerticalBox(StaminaBar)->SetPadding(FMargin(0.0f, 2.0f, 0.0f, 8.0f));

    EquipmentText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("EquipmentText"));
    EquipmentText->SetColorAndOpacity(FSlateColor(FLinearColor::White));
    Stack->AddChildToVerticalBox(EquipmentText);

    UTextBlock* Help = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("HelpText"));
    Help->SetText(FText::FromString(TEXT("LMB: atacar   E: cambiar arma   TAB: equipo")));
    Help->SetColorAndOpacity(FSlateColor(FLinearColor(0.65f, 0.68f, 0.72f)));
    Stack->AddChildToVerticalBox(Help)->SetPadding(FMargin(0.0f, 4.0f, 0.0f, 0.0f));
}

void UTenFeHUDWidget::Refresh()
{
    if (!Character || !HealthBar || !StaminaBar || !EquipmentText)
    {
        return;
    }

    const UTenFeStatsComponent* Stats = Character->GetStats();
    const UTenFeEquipmentComponent* Equipment = Character->GetEquipment();
    HealthBar->SetPercent(Stats->GetHealthPercent());
    StaminaBar->SetPercent(Stats->GetStaminaPercent());

    const FTenFeItemDefinition Weapon = Equipment->GetEquippedWeapon();
    EquipmentText->SetText(FText::FromString(FString::Printf(
        TEXT("%s  |  Daño %.0f  |  Defensa %.0f  |  Peso %.1f"),
        *Weapon.DisplayName.ToString(), Weapon.Damage, Equipment->GetTotalDefense(), Equipment->GetEquipmentWeight())));
}
